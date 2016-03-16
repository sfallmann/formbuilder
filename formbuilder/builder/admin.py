import json
from pprint import pprint
from django.contrib import admin
from django.conf import settings
from django.utils.html import mark_safe
from django import forms
from django.db import models
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import HttpResponse
from .models import Category
from .models import FormData, FormTemplate, FieldSet
from .models import FieldTemplate, FieldChoice
from .adminforms import FieldTemplateInlineForm, FieldTemplateForm
from .adminforms import FieldSetInlineForm, FormTemplateForm
from helper.constants import field_types


class CategoryAdmin(admin.ModelAdmin):

    # Autofills the slug field based on the name field
    prepopulated_fields = {"slug": ("name",)}


class FieldTemplateFormSet(BaseInlineFormSet):

    def clean(self):
        super(FieldTemplateFormSet, self).clean()

        file_count = 0
        dz_count = 0

        #  Check through all the FieldSSet forms
        for form in self.forms:
            #  If the form doesn't have cleane_data continue
            if not hasattr(form, 'cleaned_data'):
                continue
            #  If it's the "empty" FieldSet

            #  clean the data
            data = form.cleaned_data


            type_list = [
                field_types.DROPZONE,
                field_types.FILE
            ]

            templates = FieldTemplate.objects.filter(
                form_template=form.instance.form_template,
                ).exclude(
                pk=form.instance.pk
            )

            if form.instance.field_type == field_types.DROPZONE:
                dz_count += 1

            if form.instance.field_type == field_types.FILE:
                file_count += 1

            for t in templates:
                print t.field_type
                if t.field_type == field_types.FILE and data.get('field_type') == field_types.DROPZONE:
                    raise ValidationError(
                        "You can't add a file field since the form"\
                            "has a dropzone"
                    )

                if t.field_type == field_types.DROPZONE and data.get('field_type') in type_list:
                    raise ValidationError(
                        "You can't add a dropzone since the form "\
                            "has a dropzone or file field"
                    )

        if (dz_count and file_count) or dz_count > 1:
            raise ValidationError(
                "You can't add multiple dropzones or a dropzone with file fields."
            )



class FieldTemplateInline(admin.StackedInline):
    model = FieldTemplate
    form = FieldTemplateInlineForm
    formset = FieldTemplateFormSet
    show_change_link = True
    extra = 0
    fieldsets = (
        ("Options",
         {  'classes': ("collapse",),
            'fields': ('name', 'label',('field_type','position','css_class'),'field_set',)
            }
        ),
    )


    def get_formset(self, request, obj, **kwargs):

        # only show the fields in the common to all field types
        self.fields = [
            "name",
            "form_template",
            "field_type",
            "field_set",
            "label",
            "css_class",
            "position",
        ]

        return super(
            FieldTemplateInline, self).get_formset(request, obj, **kwargs)

    #  order the fields by field set membership and then position
    def get_queryset(self, request):
            return super(
                FieldTemplateInline, self
            ).get_queryset(request).order_by('field_set', 'position')

    #  only show FieldSets that are related to the fields' FormTemplate
    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "field_set":
            try:
                # id of the FormTemplate
                parent_obj_id = request.resolver_match.args[0]
                form_template = FormTemplate.objects.get(id=parent_obj_id)

                kwargs["queryset"] = FieldSet.objects.filter(
                    form_template=form_template
                )

            except IndexError:
                kwargs["queryset"] = FieldSet.objects.none()

        return super(FieldTemplateInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs)



class FieldChoiceInline(admin.StackedInline):
    model = FieldChoice
    extra = 1


class FieldTemplateAdmin(admin.ModelAdmin):

    form = FieldTemplateForm
    list_display = (
        'name',
        'label',
        'field_type',
        'field_set',
        'position',
        'form_template',
        'form_template_link',
    )

    list_editable =('label', 'field_set', 'position')
    ordering = (
        'field_set', 'form_template', 'position', 'field_type', 'name')
    list_filter = ('form_template', 'field_set',)
    save_on_top = True
    show_add_link = False


    def has_add_permission(self, request):
        return False

    def get_form(self, request, obj, **kwargs):

        #  fields common to all field types
        self.fields = [
            "name",
            #"form_template",
            "field_type",
            "field_set",
            "label",
            "css_class",
            "position",
        ]

        #  if this is for an existing FieldTemplate
        print kwargs
        if obj:
            #  define the fields common to all FieldTemplates
            #  TODO:  Need to make this into a constant
            common = [
                #"form_template",
                "field_set",
                "field_type",
                "name",
                "label",
                "css_class",
                "position",
            ]
            #  get all the availabled fields based on the value of field_type
            #  and then sort them.

            if obj.field_type == "email":
                common.append("send_confirmation")

            field_types.ATTRS[obj.field_type].sort()
            #  add the additional fields with common
            self.fields = common + field_types.ATTRS[obj.field_type]
            #  add FieldChoiceInline for select and radio field types
            if obj.field_type == "select" or obj.field_type == "radio":
                self.inlines = [FieldChoiceInline, ]

        return super(FieldTemplateAdmin, self).get_form(request, obj, **kwargs)

    def form_template_link(self, obj):

        link = obj.form_template.get_admin_change_url()


        return mark_safe("<a href='%s'>Link</a>" % link)


class FieldSetFormSet(BaseInlineFormSet):

    def clean(self):
        super(FieldSetFormSet, self).clean()

        #  Check through all the FieldSSet forms
        for form in self.forms:
            #  If the form doesn't have cleane_data continue
            if not hasattr(form, 'cleaned_data'):
                continue
            #  If it's the "empty" FieldSet

            #  clean the data
            data = form.cleaned_data

            try:
                fs = FieldSet.objects.get(form_template=form.instance.form_template, name=settings.EMPTY_FIELDSET)

                if form.instance.pk == fs.pk:

                    #  if the the name has been changed raise and error
                    if(data.get('name') != settings.EMPTY_FIELDSET):

                        raise ValidationError(
                            'FieldSet %s cannot be renamed!' %
                            settings.EMPTY_FIELDSET
                        )
                    #  if the the name has been changed raise and error
                    if(data.get('label')):

                        raise ValidationError(
                            'FieldSet %s cannot be given a label!' %
                            settings.EMPTY_FIELDSET
                        )

                    #  if the delete button is checked raise and error
                    if (data.get('DELETE')):
                        raise ValidationError(
                            'FieldSet %s can never be deleted!' %
                            settings.EMPTY_FIELDSET
                        )

            except ObjectDoesNotExist:

                if(data.get('name') == settings.EMPTY_FIELDSET):

                    raise ValidationError(
                        '{efs} is a reserved name.  A FieldSet with the name {efs}'\
                        ' will be created once the FormTemplate is saved.'.format(
                            efs=settings.EMPTY_FIELDSET
                        )
                    )


class FieldSetInline(admin.StackedInline):

    model = FieldSet
    form = FieldSetInlineForm
    formset = FieldSetFormSet
    show_change_link = False

    extra = 0

    fieldsets = (
        (None, {
            'fields': (('name', 'label', 'position'))
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('legend',),
        }),
    )
    def get_queryset(self, request):
            return super(
                FieldSetInline, self
            ).get_queryset(request).order_by('position')


class FormTemplateAdmin(admin.ModelAdmin):
    form = FormTemplateForm
    inlines = [FieldSetInline, FieldTemplateInline, ]
    save_on_top = True
    fieldsets = (
        (None, {
            'fields': (
                    'name',
                    'category',
                    'notification_list',
                    'login_required',
                )
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': (('background_color', 'text_color'),'header', 'footer'),
        }),
    )


class FormDataAdmin(admin.ModelAdmin):
    list_display = ("__str__", "form_template", "data_category")
    ordering = ('form_template', 'id')
    readonly_fields = ["form_template", "data", "formatted_data","data_category"]

    # allows for sotring by Category
    def data_category(self, obj):

        if obj.form_template:
            return obj.form_template.category
        else:
            return None

    data_category.short_description = "Category"

    def formatted_data(self, obj):

        return json.dumps(
            obj.data,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )



admin.site.register(Category, CategoryAdmin)
admin.site.register(FieldTemplate, FieldTemplateAdmin)
admin.site.register(FormTemplate, FormTemplateAdmin)
admin.site.register(FormData, FormDataAdmin)
