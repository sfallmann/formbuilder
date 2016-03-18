import json
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from crispy_forms.layout import HTML, Div
from crispy_forms.bootstrap import Accordion, AccordionGroup, Tab
from django import forms
from django.conf import settings
from django.utils.html import format_html
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from builder.models import FormTemplate, FieldTemplate, FieldSet
from helper.constants import field_types


FILE_LABEL = "<label for='{name}' class='control-label'>{label}</label>"
FILE_HTML = "<input name='{name}' id='{name}' type=file id='{name}'"\
                "{multiple} data-maxfiles='{maxfiles}'"\
                    "class='form-control form-style {css_class}'/>"




class Form(forms.Form):

    def __init__(self, obj, *args, **kwargs):

        super(Form, self).__init__(*args, **kwargs)

        self.exclusions = [
            "html", "file"
        ]

        self.confirmation_keys = []

        self.get_absolute_url = obj.get_absolute_url
        self.helper = FormHelper()

        self.helper.form_id = "fb-form"
        self.helper.form_method = 'post'

        self.helper.background_color = obj.background_color
        self.helper.text_color = obj.text_color
        self.helper.form_action = obj.get_absolute_url()
        if obj.dropzone:
            self.template = "dropzone_form.html"
            self.helper.form_class = "form-style dropzone"

        else:
            self.template = "fileinput_form.html"
            self.helper.form_class = "form-style"


        field_templates = obj.field_templates.all().order_by(
            'field_set', 'position')

        for template in field_templates:
            if template.field_type not in self.exclusions:
                self.fields[template.name] = self.create_field(template)

        layout = self.helper.layout = Layout()

        self.create_fieldsets(obj)

        self.helper.attrs = {
            'enctype': 'multipart/form-data',
        }

        recaptcha = '<div class="g-recaptcha" data-sitekey="%s">'\
            '</div>' % settings.RECAPTCHA_SITEKEY

        layout.append(HTML("{{recaptcha_error|safe}}"))

        layout.append(HTML(recaptcha))
        layout.append(HTML("<br/>"))

        layout.append(ButtonHolder
                      (Submit('submit', 'Submit', css_class='button white')))

    def clean(self):

        self.clean_files_only = {}
        self.clean_data_only = {}
        self.file_list = []
        self.confirmation_list = []

        cleaned_data = super(Form, self).clean()

        file_types = [
            TemporaryUploadedFile,
            InMemoryUploadedFile,
            SimpleUploadedFile
        ]

        for key in cleaned_data.keys():

            if key in self.confirmation_keys:
                self.confirmation_list.append(cleaned_data[key])

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
            f.label = "<span style='color: red; font-size: .95em;' "\
                "class='glyphicon glyphicon-star'></span>" + f.label
            #format_html(f.label)
        empty_choice = "No choices were added to this field!"

        other_tags = [
            #field_types.PHONE,
            field_types.COUNTRY,
            field_types.CHECKBOX,
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
                'class': 'form-control form-style',
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
        elif f.field_type == field_types.CHECKBOX:

            attrs.update({
                'id': f.name.lower(),
                'class': 'form-style',
                'name': f.name.lower(),
            })

            return forms.BooleanField(
                widget=forms.CheckboxInput(
                    attrs=attrs
                ),
                required=False,
                label=f.label,
                help_text=f.help_text
            )

        elif f.field_type == field_types.TEXT_AREA:

            attrs.update({
                'id': f.name.lower(),
                'class': 'form-control form-style',
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

            return _field

        elif f.field_type == field_types.COUNTRY:

            attrs.update({
                'id': f.name.lower(),
                'class': 'country-select',
                'name': f.name.lower(),
            })

            _field = forms.ChoiceField(
                required=False,
                label=f.label,
                help_text=f.help_text
            )

            _field.widget.attrs.update(attrs)

            return _field



    def create_html(self, template):

        if template.field_type == field_types.HTML:

            return template.html

        elif template.field_type == field_types.FILE:

            multiple=""

            if template.maxfiles > 1:
                multiple="multiple"

            file_label = FILE_LABEL.format(
                name=template.name,
                label=template.label
            )

            file_html = FILE_HTML.format(
                name=template.name,
                multiple=multiple,
                maxfiles=template.maxfiles,
                css_class=template.css_class
            )

            return file_label + file_html



    def create_fieldsets(self, obj):

        for fset in obj.fieldsets.all().order_by('position'):

            _templates = fset.field_templates.all().order_by('position')

            #values = ["<p style='font-size=2em;'>%s</p>" % str(fset.label)]

            values = []
            if fset.accordion:
                values =[str(fset.label + " (click)"),]
            else:
                values =[str(fset.label),]

            for t in _templates:
                if t.field_type in self.exclusions:
                    values.append(HTML(self.create_html(t)))
                else:
                    if t.field_type == "email":
                        if t.send_confirmation:
                            self.confirmation_keys.append(t.name)
                    values.append(
                        Div(
                            str(t.name),
                            css_class=t.css_class
                        )
                    )

            if fset.accordion:
                self.helper.layout.append(
                    Accordion(
                        AccordionGroup(*values),
                    )
                )
            else:
                self.helper.layout.append(Fieldset(*values))

            #self.helper.layout.append(HTML("<hr/>"))

