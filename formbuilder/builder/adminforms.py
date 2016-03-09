from django import forms
from django.conf import settings
from .models import FieldTemplate, FieldSet, FormTemplate
from .models import FieldChoice
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget



class FormTemplateForm(forms.ModelForm):

    model = FormTemplate

    def __init__(self, *args, **kwargs):
        super(FormTemplateForm, self).__init__(*args, **kwargs)

        self.fields['notification_list'].widget = forms.TextInput(attrs={
                "type": "email",
                "style": "width: 400px;"
            })

        self.fields['header'].widget = CKEditorUploadingWidget(config_name="default",
                attrs={
                    'style': 'height: 300px; width: 600px; font-size: 1.15em;'
                }
            )

        self.fields['footer'].widget = CKEditorUploadingWidget(config_name="default",
                attrs={
                    'style': 'height: 300px; width: 600px; font-size: 1.15em;'
                }
            )


class FieldSetInlineForm(forms.ModelForm):

    model = FieldSet

    def __init__(self, *args, **kwargs):
        super(FieldSetInlineForm, self).__init__(*args, **kwargs)

        if "instance" in kwargs:
            f = kwargs["instance"]

            if f.name == settings.EMPTY_FIELDSET:

                self.fields["name"].disabled = True
                self.fields["label"].disabled = True

        self.fields['helper_text'].widget = CKEditorWidget(config_name="coding",
                attrs={
                    'style': 'height: 300px; width: 600px; font-size: 1.15em;'
                }
            )


class FieldTemplateInlineForm(forms.ModelForm):

    model = FieldTemplate

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
            #self.fields['field_set'].show_hidden_initial = True
        else:
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

            self.fields['position'] = forms.ChoiceField(choices=position_choices, required=False)
            self.fields['field_set'].queryset = FieldSet.objects.filter(
                form_template=instance.form_template)

        else:

            self.fields['field_set'].disabled = True
            self.fields['position'].disabled = True

        if 'html' in self.fields:
            self.fields['html'].widget = CKEditorUploadingWidget(config_name="default",
                attrs={
                    'style': 'height: 300px; width: 600px; font-size: 1.15em;'
                }
            )
