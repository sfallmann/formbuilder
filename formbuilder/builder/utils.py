from helper.constants import field_types


class FormFactory(form_template):

    def __init__(self):

        self.template = form_template


    def create_field(f):

        options = f.fieldtemplateoptions

        if options.required:
            options.label += "*"

        other_tags = [
            field_types.TEXT_AREA,
            field_types.FILE,
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
        elif f.field_type == field_types.TEXT_AREA:

            return forms.CharField(
                max_length=options.max_length,
                widget=forms.Textarea(
                    attrs=attrs
                ),
                required=False,
                label = options.label
            )
        elif f.field_type == field_types.FILE:

            return forms.FileField(
                max_length=options.max_length,
                required=False,
                label = options.label
            )
