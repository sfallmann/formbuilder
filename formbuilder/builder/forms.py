from django import forms
from builder.models import FormTemplate, FieldTemplate, FieldSet
from helper.constants import input_types
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit

def create_field(f):

    options = f.fieldtemplateoptions

    if options.required:
        options.label += "*"

    other_tags = [
        input_types.TEXT_AREA,
        input_types.FILE,
    ]

    if options.autocomplete:
        autocomplete = "on"
    else:
        autocomplete = "off"


    attrs={
        'id': f.name.lower(),
        'class': 'form-control',
        'placeholder': options.placeholder,
        'autocomplete': autocomplete,
        'name': f.name.lower(),
        'type': f.field_type,
        "required": options.required,

    }

    if f.field_type not in other_tags:

        return forms.CharField(
            max_length=options.max_length,
            widget=forms.TextInput(
                attrs=attrs
            ),
            required=False,
            label = options.label
        )
    elif f.field_type == input_types.TEXT_AREA:

        return forms.CharField(
            max_length=options.max_length,
            widget=forms.Textarea(
                attrs=attrs
            ),
            required=False,
            label = options.label
        )
    elif f.field_type == input_types.FILE:

        return forms.FileField(
            max_length=options.max_length,
            required=False,
            label = options.label
        )


class Form(forms.Form):

    def __init__(self, obj, *args, **kwargs):

        super(Form, self).__init__(*args, **kwargs)
        self.helper = FormHelper()


        field_templates = obj.field_templates.all().order_by('field_set','position')
        self.get_absolute_url = obj.get_absolute_url

        key_order = []

        for template in field_templates:
            self.fields[template.name] = create_field(template)
            key_order.append(template.name)

        self.fields.keyOrder=key_order

        layout = self.helper.layout = Layout()


        obj_fieldsets = FieldSet.objects.filter(form_template=obj)


        for fset in obj_fieldsets:

            _templates = FieldTemplate.objects.filter(
                form_template=obj, field_set=fset).order_by('position')

            values = [str(fset.name)]

            for t in _templates:
                values.append(str(t.name))
            layout.append(Fieldset(*values))

        _templates = FieldTemplate.objects.filter(
                form_template=obj, field_set=None).order_by('position')

        self.helper.form_id = obj.name
        self.helper.form_method = 'post'
        self.helper.form_action = obj.get_absolute_url()
        self.helper.attrs = {'enctype': 'multipart/form-data'}

        layout.append(ButtonHolder
                      (Submit('submit', 'Submit', css_class='button white')))

