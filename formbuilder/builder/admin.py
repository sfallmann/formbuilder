from django.contrib import admin
from django.utils.html import mark_safe
from django import forms
from .models import Category
from .models import FormTemplate, FormData
from .models import FormTemplateOptions, FieldSet
from .models import FieldTemplate, FieldTemplateOptions
from helper.constants import input_types

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class FieldTemplateOptionsInline(admin.StackedInline):
    model = FieldTemplateOptions
    show_change_link = True

    def get_formset(self, request, obj, **kwargs):

        type_ = obj.field_type
        common_fields = ('autofocus','required')
        input_tag_common_fields = (
            'autocomplete','disabled','max_length','placeholder','read_only'
        )
        input_specific_fields = ('min_length', 'pattern')
        numeric_specific_fields = ('min_value', 'max_value')
        checkbox_specific_fields = ('checked')

        self.fieldsets = (
            (None, {
                    'fields': common_fields
                }),
        )
        if type_ == input_types.TEXT:
            type_fields = input_tag_common_fields + input_specific_fields
            self.fieldsets += (
                ('Text Specific', {
                           'classes': ('collapse',),
                            'fields': type_fields
                    }),
            )

        return super(FieldTemplateOptionsInline, self).get_formset(request, obj, **kwargs)

    def has_delete_permission(self, request, obj):
        return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "formset":
            try:
                parent_obj_id = request.resolver_match.args[0]
                _field = FieldTemplate.objects.get(id=parent_obj_id)
                kwargs["queryset"] = FieldSet.objects.filter(form_template=_field.form_template)
            except IndexError:
                kwargs["queryset"] = FieldSet.objects.none()
        return super(
            FieldTemplateOptionsInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class FieldTemplateInline(admin.StackedInline):
    model = FieldTemplate
    show_change_link = True
    extra = 1


class FieldTemplateAdmin(admin.ModelAdmin):

    list_display = ('name', 'field_type', 'form_template')
    ordering = ('form_template', 'field_type', 'name')
    inlines = [FieldTemplateOptionsInline,]



class FieldSetInline(admin.TabularInline):

    model = FieldSet
    show_change_link = True
    extra = 1


class FormTemplateOptionsInline(admin.TabularInline):

    model = FormTemplateOptions
    show_change_link = True

    def has_delete_permission(self, request, obj):
        return False


class FormTemplateAdmin(admin.ModelAdmin):

    inlines = [FormTemplateOptionsInline, FieldSetInline, FieldTemplateInline,]


class FormDataAdmin(admin.ModelAdmin):

    readonly_fields = ["form_template", "data"]


admin.site.register(Category, CategoryAdmin)
admin.site.register(FieldTemplate, FieldTemplateAdmin)
admin.site.register(FormTemplate, FormTemplateAdmin)
admin.site.register(FormData, FormDataAdmin)
