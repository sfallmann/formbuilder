from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.conf import settings
from .models import FieldTemplate, FieldSet, FormTemplate
from .models import FieldChoice


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


class FieldTemplateForm(forms.ModelForm):

    model = FieldTemplate

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

