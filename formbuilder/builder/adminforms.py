from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.conf import settings
from django.db.models.query_utils import Q
from django.core.exceptions import ValidationError
from .models import FieldTemplate, FieldSet, FormTemplate
from .models import FieldChoice
from helper.constants import field_types


class FormTemplateForm(forms.ModelForm):

    model = FormTemplate

    def __init__(self, *args, **kwargs):
        super(FormTemplateForm, self).__init__(*args, **kwargs)

        #  setting the widget to increase the width of the field
        self.fields['notification_list'].widget = forms.TextInput(attrs={
                "type": "email",
                "style": "width: 400px;"
            })

        #  changing the widget from the default
        self.fields['header'].widget = CKEditorUploadingWidget(
            config_name="default",
            attrs={
                'style': 'height: 300px; width: 600px; font-size: 1.15em;'
            }
        )
        #  changing the widget from the default
        self.fields['footer'].widget = CKEditorUploadingWidget(
            config_name="default",
            attrs={
                'style': 'height: 300px; width: 600px; font-size: 1.15em;'
            }
        )

    def clean(self):

        cleaned_data = super(FormTemplateForm, self).clean()
        name = cleaned_data["name"]
        dropzone = cleaned_data["dropzone"]

        file_fields = FieldTemplate.objects.filter(
            field_type=field_types.FILE,
            form_template__name=name
        )

        if dropzone and file_fields:
            raise ValidationError(
                "You can't enable a dropzone on a form containing file fields."
            )


class FieldSetInlineForm(forms.ModelForm):

    model = FieldSet

    def __init__(self, *args, **kwargs):
        super(FieldSetInlineForm, self).__init__(*args, **kwargs)


        #  checking if this a new or previously created
        if "instance" in kwargs:
            f = kwargs["instance"]

            #  get the queryset of all FieldSets for the FormTemplate
            #  the instance belongs
            fieldsets = FieldSet.objects.filter(
                form_template=f.form_template)

            #  get the count
            count = fieldsets.count()
            #  set value to the position of the instance "f"
            value = f.position

            #  create a list of choices for all the positions available
            choices = ([(x, x) for x in range(1, count+1)])

            #  set the form field with the choices for position
            self.fields['position'] = forms.ChoiceField(
                choices=(choices), required=False, initial=value
            )

            #  show the initial value in the field
            self.fields['position'].show_hidden_initial = True

            if f.name == settings.EMPTY_FIELDSET:
                self.fields['label'].widget.attrs['readonly'] = True
                self.fields['name'].widget.attrs['readonly'] = True

        else:
            #  new instances have position disabled
            self.fields['position'].disabled = True



class FieldTemplateInlineForm(forms.ModelForm):

    model = FieldTemplate

    # del self.fields['field_for_item'] for dynamic fields

    def __init__(self, *args, **kwargs):

        super(FieldTemplateInlineForm, self).__init__(*args, **kwargs)

        #  checking if this a new or previously created
        if "instance" in kwargs:

            f = kwargs["instance"]

            #  get the queryset of all FieldTemplates for the FormTemplate
            #  and FieldSet the instance belongs
            fields = FieldTemplate.objects.filter(
                form_template=f.form_template, field_set=f.field_set)

            #  get the count
            count = fields.count()
            #  set value to the position of the instance "f"
            value = f.position

            #  create a list of choices for all the positions available
            choices = ([(x, x) for x in range(1, count+1)])

            #  set the form field with the choices for position
            self.fields['position'] = forms.ChoiceField(
                choices=(choices), required=False, initial=value
            )

            #  show the initial value in the field
            self.fields['position'].show_hidden_initial = True

        else:

            #  new instances have position disabled
            self.fields['position'].disabled = True

    def clean(self):

        cleaned_data = super(FieldTemplateInlineForm, self).clean()

        form_template = cleaned_data["form_template"]
        field_type = cleaned_data["field_type"]

        if form_template.dropzone and field_type == field_types.FILE:
            raise ValidationError(
                "You can't add file fields to a form with a dropzone."
            )

class FieldTemplateForm(forms.ModelForm):

    model = FieldTemplate

    def __init__(self, *args, **kwargs):

        super(FieldTemplateForm, self).__init__(*args, **kwargs)

        self.fields["field_set"].empty_label = None

        instance = kwargs.get('instance')

        if instance:

            fields = FieldTemplate.objects.filter(
                form_template=instance.form_template,
                field_set=instance.field_set
            )

            count = fields.count()

            position_choices = ([(x, x) for x in range(1, count+1)])

            self.fields['position'] = forms.ChoiceField(
                choices=position_choices,
                required=False
            )
            self.fields['field_set'].queryset = FieldSet.objects.filter(
                form_template=instance.form_template)

        else:

            self.fields['field_set'].disabled = True
            self.fields['position'].disabled = True

        if 'html' in self.fields:
            self.fields['html'].widget = forms.Textarea(
                attrs={
                    'style': 'height: 300px; width: 600px; font-size: 1.15em;'
                }
            )
    def clean(self):

        cleaned_data = super(FieldTemplateForm, self).clean()

        if "field_set" in cleaned_data:
            field_set = cleaned_data["field_set"]
            form_template = field_set.form_template.dropzone
            field_type = cleaned_data['field_type']

            if field_set.form_template.dropzone and field_type == field_types.FILE:
                raise ValidationError(
                    "You can't add file fields to a form with a dropzone."
                )

