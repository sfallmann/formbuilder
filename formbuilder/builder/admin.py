from django.contrib import admin
from django.utils.html import mark_safe
from django import forms
from .models import Department
from .models import FormTemplate, FormData
from .models import FormTemplateOptions, FieldSet
from .models import FieldTemplate, FieldTemplateOptions


class FieldTemplateOptionsInlineForm(forms.ModelForm):



    def __init__(self, *args, **kwargs):
        super(FieldTemplateOptionsInlineForm, self).__init__(*args, **kwargs)
        print self.instance
        # _form_template = self.instance.field_template.form_template
        #self.fields['formset'].queryset = FormSet.objects.filter(form_template=_form_template)

class DepartmentAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class FieldTemplateOptionsInline(admin.TabularInline):
    model = FieldTemplateOptions
    show_change_link = True

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


class FormTemplateOptionsInline(admin.StackedInline):

    model = FormTemplateOptions
    show_change_link = True


class FormTemplateAdmin(admin.ModelAdmin):

    inlines = [FormTemplateOptionsInline, FieldSetInline, FieldTemplateInline,]


class FormDataAdmin(admin.ModelAdmin):

    readonly_fields = ["form_template", "data"]


admin.site.register(Department, DepartmentAdmin)
admin.site.register(FieldTemplate, FieldTemplateAdmin)
admin.site.register(FormTemplate, FormTemplateAdmin)
admin.site.register(FormData, FormDataAdmin)
