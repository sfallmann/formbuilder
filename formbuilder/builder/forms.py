import json
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML
from django import forms
from django.conf import settings
from django.utils.html import format_html
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from builder.models import FormTemplate, FieldTemplate, FieldSet
from helper.constants import field_types


FILE_LABEL = "<label for='{name}' class='control-label'>{label}</label>"
FILE_HTML = "<input name='{name}' id='{name}' type=file id='file'"\
                "{multiple} data-maxfiles='{maxfiles}' class='form-control'/>"


class Form(forms.Form):

    def __init__(self, obj, *args, **kwargs):

        super(Form, self).__init__(*args, **kwargs)

        self.exclusions = [
            "html", "file"
        ]

        self.get_absolute_url = obj.get_absolute_url
        self.helper = FormHelper()

        field_templates = obj.field_templates.all().order_by(
            'field_set', 'position')

        for template in field_templates:
            if template.field_type not in self.exclusions:
                self.fields[template.name] = self.create_field(template)

        layout = self.helper.layout = Layout()

        self.create_fieldsets(obj)

        self.helper.form_id = "form_%s" % obj.id
        self.helper.form_method = 'post'
        self.helper.form_action = obj.get_absolute_url()
        self.helper.attrs = {'enctype': 'multipart/form-data'}

        recaptcha = '<hr/><div class="g-recaptcha" data-sitekey="%s">'\
            '</div>' % settings.RECAPTCHA_SITEKEY

        layout.append(HTML("{{recaptcha_error|safe}}"))

        layout.append(HTML(recaptcha))
        layout.append(HTML("<hr/>"))

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

    def create_field(self, f):

        if f.required and f.label:
            f.label += "<span class='glyphicon glyphicon-star'></span>"
            #format_html(f.label)
        empty_choice = "No choices were added to this field!"

        other_tags = [

            field_types.FILE,
            field_types.RADIO,
            field_types.SELECT,
            field_types.TEXT_AREA,
            field_types.DROPZONE

        ]

        if f.autocomplete:
            autocomplete = "on"
        else:
            autocomplete = "off"

        attrs = {}
        initial = None

        if f.field_type == "select" or f.field_type == "radio":
            field_choices = f.field_choices.all()

            choices = [(c.key, c.value) for c in field_choices]

            if not choices:
                choices = [
                    (empty_choice, empty_choice)
                ]

            initial = choices[0][0]

        for a in field_types.ATTRS[f.field_type]:

            if a == "pattern":

                if getattr(f, a):
                    attrs.update({a: getattr(f, a)})

            elif a == 'accept':

                if getattr(f, a):
                    accept = ",".join(getattr(f, a))
                    attrs.update({a: accept})

            else:

                attrs.update({a: getattr(f, a)})

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
                label=f.label,
                help_text=f.help_text
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
                label=f.label,
                help_text=f.help_text
            )

        elif f.field_type == field_types.RADIO:

            _field = forms.ChoiceField(
                widget=forms.RadioSelect,
                choices=choices,
                required=False,
                label=f.label,
                initial=initial,
                help_text=f.help_text
            )

            _field.widget.attrs.update(attrs)

            return _field

        elif f.field_type == field_types.SELECT:

            _field = forms.ChoiceField(
                choices=choices,
                required=False,
                label=f.label,
                initial=initial,
                help_text=f.help_text
            )

            _field.widget.attrs.update(attrs)

        elif f.field_type == field_types.DROPZONE:

            return forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        "type": "hidden",
                        "name": f.name,
                        "id": "add-dropzone",
                        "required": f.required,
                        "data-limit": f.maxvalue
                    }
                ),
                required=False,
            )


            return _field


    def create_html(self, template):

        print template.field_type
        if template.field_type == "html":
            print template.html
            return template.html

        elif template.field_type == field_types.FILE:

            multiple = ""

            if template.maxfiles > 1:
                multiple = "multiple"

            file_label = FILE_LABEL.format(
                name=template.name,
                label=template.label
            )

            file_html = FILE_HTML.format(
                name = template.name,
                multiple = multiple,
                maxfiles = template.maxfiles
            )

            return file_label + file_html


    def create_fieldsets(self, obj):

        for fset in obj.fieldsets.all().order_by('position'):

            _templates = fset.field_templates.all().order_by('position')

            #values = ["<p style='font-size=2em;'>%s</p>" % str(fset.label)]

            values = []

            values =[str(fset.help_text),]

            for t in _templates:
                if t.field_type in self.exclusions:
                    values.append(HTML(self.create_html(t)))
                else:
                    values.append(str(t.name))
            if values:

                if fset.label:
                    self.helper.layout.append(
                        HTML("<h2>%s</h2>" % fset.label)
                    )


                self.helper.layout.append(Fieldset(*values))

