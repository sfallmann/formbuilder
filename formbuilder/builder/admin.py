from django.contrib import admin
from django.utils.html import mark_safe
from django import forms
from .models import Category
from .models import FormTemplate, FormData
from .models import FormTemplateOptions, FieldSet
from .models import FieldTemplate, FieldTemplateOptions
from helper.constants import input_types


class FieldTemplateInlineForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):

        super(FieldTemplateInlineForm, self).__init__(*args, **kwargs)

        if "instance" in kwargs:
            f = kwargs["instance"]
            fields = FieldTemplate.objects.filter(
                form_template=f.form_template, field_set=f.field_set)
            count = fields.count()
            value = f.position

            choices = ([(x, x) for x in range(1, count+1)])

            self.fields['position'] = forms.ChoiceField(choices=(choices), required=False, initial=value)
            self.fields['position'].show_hidden_initial = True
        else:
            self.fields['position'].disabled = True

class FieldTemplateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        super(FieldTemplateForm, self).__init__(*args, **kwargs)

        instance = kwargs.get('instance')


        if instance:

            fields = FieldTemplate.objects.filter(
                form_template=instance.form_template,
                field_set=instance.field_set
            )

            count = fields.count()

            position_choices = ([(x, x) for x in range(1, count+1)])

            self.fields['position'] = forms.ChoiceField(choices=position_choices, required=False)
            self.fields['field_set'].queryset = FieldSet.objects.filter(
                form_template=instance.form_template)
        else:

            form_template = None
            fields = FieldTemplate.objects.filter(field_set=None)
            count = fields.count() + 1

            self.fields['position'].disabled = True






class CategoryAdmin(admin.ModelAdmin):

    prepopulated_fields = {"slug": ("name",)}


class FieldTemplateOptionsInline(admin.StackedInline):

    model = FieldTemplateOptions
    show_change_link = True

    def get_formset(self, request, obj, **kwargs):

        common_fields = ('label','autofocus','required')

        self.fieldsets = (
            (None, {
                    'fields': common_fields
                }),
        )

        if obj:
            type_ = obj.field_type

            input_tag_common_fields = (
                'autocomplete','disabled','max_length','placeholder','read_only'
            )
            input_specific_fields = ('min_length', 'pattern')
            numeric_specific_fields = ('min_value', 'max_value')
            checkbox_specific_fields = ('checked')


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


class FieldTemplateInline(admin.StackedInline):
    model = FieldTemplate
    form = FieldTemplateInlineForm
    show_change_link = True
    extra = 0


    def get_queryset(self, request):
            return super(FieldTemplateInline, self).get_queryset(request).order_by('field_set','position')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "field_set":
            try:
                parent_obj_id = request.resolver_match.args[0]
                form_template = FormTemplate.objects.get(id=parent_obj_id)
                kwargs["queryset"] = FieldSet.objects.filter(form_template=form_template)
            except IndexError:
                kwargs["queryset"] = FieldSet.objects.none()

        return super(FieldTemplateInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs)


class FieldTemplateAdmin(admin.ModelAdmin):

    form = FieldTemplateForm
    list_display = ('name', 'field_type', 'form_template','field_set','position')
    ordering = ('position','field_set','form_template','field_type','name')
    list_filter = ('form_template','field_set',)
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
