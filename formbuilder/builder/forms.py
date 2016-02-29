from django import forms
from builder.models import FormTemplate, FieldTemplate
from helper.constants import input_types


def create_field(f):

    _label = f.name.title()
    _placeholder = ""
    _autocomplete = "off"

    if hasattr(f, 'fieldtemplateoptions'):
        _options = f.fieldtemplateoptions

        if _options.label:
            _label = _options.label
        else:
            _label = ""

        _placeholder = _options.placeholder

        if _options.autocomplete:
            _autocomplete = "on"

    _attrs={
        'id': f.name.lower(),
        'class': 'test',
        'placeholder': _placeholder,
        'autocomplete': _autocomplete,
        'name': f.name.lower(),
        'type': f.field_type
    }

    if f.field_type == input_types.TEXT:
        return forms.CharField(
            max_length=f.max_length,
            widget=forms.TextInput(
                attrs=_attrs
            ),
            label = _label

        )


class Form(forms.Form):



    def __init__(self, obj, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        _fields = obj.field_templates.all()
        self.get_absolute_url = obj.get_absolute_url
        for _field in _fields:
            self.fields[_field.name] = create_field(_field)





