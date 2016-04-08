import json
import csv
from StringIO import StringIO
from zipfile import ZipFile
from pprint import pprint
from datetime import datetime
from guardian.admin import GuardedModelAdmin
from django.contrib import admin
from django.conf import settings
from django.utils.text import slugify
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

        use_as_prefix_list  = []

        for form in self.forms:

            if not hasattr(form, 'cleaned_data'):
                continue

            data = form.cleaned_data
            use_as_prefix = data.get('use_as_prefix')
            name = str(data.get("name"))

            if(use_as_prefix):

                use_as_prefix_list.append(name)

                if len(use_as_prefix_list) > 1:
                    raise ValidationError(
                        "Only one FieldTemplate can be 'used as prefix': "\
                            "check FieldTemplates %s" % str(use_as_prefix_list)
                    )


class FieldTemplateInline(admin.StackedInline):

    model = FieldTemplate
    #formset = FieldTemplateFormSet
    form = FieldTemplateInlineForm
    show_change_link = True
    extra = 0
    fieldsets = (
        (None, {
            'fields': (('name', 'label'), ('field_set','field_type','position','css_class',)),
        }),
    )

    def get_formset(self, request, obj, **kwargs):

        fs = super(
            FieldTemplateInline, self).get_formset(request, obj, **kwargs)

        print fs.form.__dict__

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


        return fs


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
        'field_set',
        'css_class',
        'use_as_prefix',
        'position',
        'required',
        'form_template_link',
    )

    list_editable =('css_class', 'position',)
    ordering = (
        'form_template', 'field_set', 'position', 'css_class')
    list_filter = ('form_template', 'field_set',)
    save_on_top = True
    show_add_link = False


    def has_add_permission(self, request):
        return False

    def get_form(self, request, obj, **kwargs):

        #  fields common to all field types
        self.fields = [
            "name",
            "field_type",
            "field_set",
            "label",
            "css_class",
            "position",
        ]

        #  if this is for an existing FieldTemplate

        if obj:
            #  define the fields common to all FieldTemplates
            #  TODO:  Need to make this into a constant
            common = [
                "field_set",
                "field_type",
                "name",
                "label",
                "css_class",
                "position",
            ]
            #  get all the availabled fields based on the value of field_type
            #  and then sort them.

            field_types.ATTRS[obj.field_type].sort()
            #  add the additional fields with common
            self.fields = common + field_types.ATTRS[obj.field_type]
            #  add FieldChoiceInline for select and radio field types
            if obj.field_type == "select" or obj.field_type == "radio":
                self.inlines = [FieldChoiceInline, ]

        return super(FieldTemplateAdmin, self).get_form(request, obj, **kwargs)

    def form_template_link(self, obj):

        link = obj.form_template.get_admin_change_url()
        return mark_safe("<a href='%s'>%s</a>" % (link, obj.form_template))


class FieldSetFormSet(BaseInlineFormSet):

    def clean(self):
        super(FieldSetFormSet, self).clean()

        #  Check through all the FieldSSet forms
        for form in self.forms:
            #  If the form doesn't have cleaned_data continue
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
            'fields': (('name', 'label'), ('position', 'accordion')),
        }),
    )
    def get_queryset(self, request):
            return super(
                FieldSetInline, self
            ).get_queryset(request).order_by('position')


class FormTemplateAdmin(GuardedModelAdmin):
    form = FormTemplateForm
    inlines = [FieldSetInline, FieldTemplateInline, ]
    actions = ["copy_form", "export_to_zipped_csv"]
    save_on_top = True
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {
            'fields': (
                    'name',
                    'slug',
                    'category',
                    'notification_list',
                    'login_required',
                    'dropzone',
                )
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('page_background_css',('background_color', 'text_color'),'header', 'footer'),
        }),
    )


    def copy_form(self, request, queryset):

        for obj in queryset:

            now = datetime.now()
            now_string = now.strftime("%y%d%m%H%M%S%f")
            new_form = FormTemplate.objects.get(pk=obj.pk)
            new_form.name = "FT_" + now_string
            new_form.slug = slugify(new_form.name)
            new_form.pk = None
            new_form.save()

            for fs in obj.fieldsets.all():

                if fs.name != 'no_fieldset':
                    new_fs = FieldSet.objects.get(pk=fs.pk)
                    new_fs.pk = None
                    new_fs.form_template = new_form
                    new_fs.save()
                else:
                    new_fs = FieldSet.objects.get(form_template=new_form, name='no_fieldset')

                for ft in fs.field_templates.all():
                    new_ft = FieldTemplate.objects.get(pk=ft.pk)
                    new_ft.pk = None
                    new_ft.form_template = new_form
                    new_ft.field_set = new_fs
                    new_ft.save()

    def export_to_zipped_csv(self, request, queryset):

        in_memory = StringIO()
        zip = ZipFile(in_memory, "a")

        for obj in queryset:


            form_data = FormData.data_objects.filter(form_template=obj)


            fieldnames = []

            for ft in obj.field_templates.all():

                fieldnames.append(str(ft.name))

            fieldnames.sort()
            now = datetime.now()
            now_string = now.strftime("%y%d%m%H%M%S%f")


            csvfile = StringIO()
            writer = csv.DictWriter(csvfile,fieldnames=fieldnames,dialect='excel')

            writer.writeheader()

            for data in form_data:
                fields = data.data["fields"]
                writer.writerow(data.data["fields"])

            zip.writestr(now_string + '.csv', csvfile.getvalue())

        # fix for Linux zip files read in Windows
        for file in zip.filelist:
            file.create_system = 0

        zip.close()

        response = HttpResponse(content_type="application/zip")
        response["Content-Disposition"] = "attachment; filename=exports.zip"

        in_memory.seek(0)
        response.write(in_memory.read())

        return response

    export_to_zipped_csv.short_description = "Export to CSV (zipped)"
    copy_form.short_description = "Copy Form Template"




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
