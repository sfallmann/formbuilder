from django import forms
from builder.models import FormTemplate, FieldTemplate
from helper.constants import input_types


def create_field(f):

    options = f.fieldtemplateoptions

    other_tags = [
        input_types.TEXT_AREA
    ]

    if options.autocomplete:
        autocomplete = "on"
    else:
        autocomlete = "off"


    attrs={
        'id': f.name.lower(),
        'class': 'test',
        'placeholder': options.placeholder,
        'autocomplete': autocomplete,
        'name': f.name.lower(),
        'type': f.field_type,
        'required': options.required
    }

    if f.field_type not in other_tags:

        return forms.CharField(
            max_length=options.max_length,
            widget=forms.TextInput(
                attrs=attrs
            ),
            label = options.label
        )
    elif f.field_type == input_types.TEXT_AREA:

        return forms.CharField(
            max_length=options.max_length,
            widget=forms.Textarea(
                attrs=attrs
            ),
            label = options.label
        )


class Form(forms.Form):



    def __init__(self, obj, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        field_templates = obj.field_templates.all()
        self.get_absolute_url = obj.get_absolute_url
        for template in field_templates:
            self.fields[template.name] = create_field(template)





