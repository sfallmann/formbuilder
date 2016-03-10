import json
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from builder.models import FormTemplate, FieldTemplate, FieldSet
from helper.constants import field_types
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML


class Form(forms.Form):

    def __init__(self, obj, *args, **kwargs):

        super(Form, self).__init__(*args, **kwargs)

        self.helper = FormHelper()

        field_templates = obj.field_templates.all().order_by(
            'field_set', 'position')
        self.get_absolute_url = obj.get_absolute_url

        key_order = []

        for template in field_templates:
            if template.field_type != "html":
                self.fields[template.name] = create_field(template)

        layout = self.helper.layout = Layout()

        obj_fieldsets = FieldSet.objects.filter(form_template=obj)

        for fset in obj_fieldsets:

            _templates = FieldTemplate.objects.filter(
                form_template=obj, field_set=fset).order_by('position')

            values = [str(fset.label)]
            if fset.helper_text:
                values.append(HTML(fset.helper_text))

            for t in _templates:
                if t.field_type =='html':
                    values.append(HTML(t.f.html))
                else:
                    values.append(str(t.name))

            layout.append(Fieldset(*values))

        _templates = FieldTemplate.objects.filter(
                form_template=obj, field_set=None).order_by('position')

        self.helper.form_id = obj.name
        self.helper.form_method = 'post'
        self.helper.form_action = obj.get_absolute_url()
        self.helper.attrs = {'enctype': 'multipart/form-data'}

        recaptcha = '<div class="g-recaptcha" data-sitekey="%s">'\
        '</div>' % settings.RECAPTCHA_SITEKEY
        layout.append(HTML("{{recaptcha_error|safe}}"))

        layout.append(HTML(recaptcha))

        layout.append(ButtonHolder
                      (Submit('submit', 'Submit', css_class='button white')))

    def clean(self):

        self.clean_files_only = {}
        self.clean_data_only = {}
        self.file_list = []

        cleaned_data = super(Form, self).clean()

        file_types = [
            TemporaryUploadedFile,
            InMemoryUploadedFile,
            SimpleUploadedFile
        ]

        for key in cleaned_data.keys():

            is_file = False

            for type_ in file_types:

                is_file = isinstance(cleaned_data[key], type_)
                if is_file:
                    break

            if is_file:

                self.clean_files_only[key] = cleaned_data[key]
                self.file_list.append(cleaned_data[key])

            else:

                self.clean_data_only[key] = cleaned_data[key]


def create_field(f):

    if f.required and f.label:
        f.label += "*"


    empty_choice = "No choices were added to this field!"

    other_tags = [

        field_types.FILE,
        field_types.RADIO,
        field_types.SELECT,
        field_types.TEXT_AREA,

    ]

    if f.autocomplete:
        autocomplete = "on"
    else:
        autocomplete = "off"

    attrs = {}
    initial = None


    if f.field_type == "select" or f.field_type == "radio":
        field_choices = f.field_choices.all()

        choices = [(c.key,c.value) for c in field_choices]

        if not choices: choices = [(empty_choice, empty_choice)]
        initial = choices[0][0]


    for a in field_types.ATTRS[f.field_type]:

        if a == "pattern":

            if getattr(f,a):
                attrs.update({a: getattr(f,a)})

        elif a == 'accept':

            if getattr(f,a):
                accept = ",".join(getattr(f,a))
                attrs.update({a: accept})

        else:

            attrs.update({a: getattr(f,a)})



    if f.field_type not in other_tags:

        attrs.update({
            'id': f.name.lower(),
            'class': 'form-control',
            'name': f.name.lower(),
            'type': f.field_type
        })

        return forms.CharField(
            max_length=f.maxlength,
            widget=forms.TextInput(
                attrs=attrs
            ),
            required=False,
            label = f.label
        )
    elif f.field_type == field_types.TEXT_AREA:

        attrs.update({
            'id': f.name.lower(),
            'class': 'form-control',
            'name': f.name.lower(),
        })

        return forms.CharField(
            max_length=f.maxlength,
            widget=forms.Textarea(
                attrs=attrs
            ),
            required=False,
            label = f.label
        )
    elif f.field_type == field_types.FILE:

        attrs.update({
            'id': f.name.lower(),
            'class': 'form-control',
            'name': f.name.lower(),
        })

        return forms.FileField(
            widget=forms.ClearableFileInput(
                attrs=attrs
            ),
            required=False,
            label = f.label

        )
    elif f.field_type == field_types.RADIO:

        _field = forms.ChoiceField(
            widget=forms.RadioSelect,
            choices=choices,
            required=False,
            label = f.label,
            initial=initial
        )

        _field.widget.attrs.update(attrs)

        return _field

    elif f.field_type == field_types.SELECT:

        _field = forms.ChoiceField(
            choices=choices,
            required=False,
            label = f.label,
            initial=initial
        )

        _field.widget.attrs.update(attrs)

        return _field


