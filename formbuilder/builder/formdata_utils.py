import re
from string import maketrans
from django.template.defaulttags import register
from .models import FormData


def create_schema(form_response):

    category = form_response.form_template.category
    form_template = form_response.form_template
    field_sets = form_template.fieldsets.all().order_by("position")

    schema = {
        "category": {
        "id":  category.id,
        "name": category.name,
        "acronym": category.acronym,
        "form_template": {
                "id":  form_template.id,
                "name": form_template.name
            }
        }
    }

    fieldset_list = []

    for field_set in field_sets:
        field_set_dict = {

            "id": field_set.id,
            "name": field_set.name,
            "label": field_set.label,
            "position": field_set.position,

        }

        field_list = []

        for field_template in field_set.field_templates.all().order_by('position'):

            field_template_dict = {

                "id": field_template.id,
                "name": field_template.name,
                "label": field_template.label,
                "position": field_template.position
            }

            field_list.append(field_template_dict)

        field_set_dict.update({ "field_templates": field_list })
        fieldset_list.append(field_set_dict)

    schema["category"]["form_template"].update({ "field_sets": fieldset_list })

    return schema


def prepare_files(posted_files):

    filenames = []
    prepped_files = []

    for file_list in posted_files:

        files = posted_files.getlist(file_list)

        for file in files:
            filenames.append(file.name)
            prepped_files.append(file)

    return {
        "prepped_files": prepped_files,
        "filenames": filenames
    }


def format_folder_prefix(value):

    if value:
        return re.sub(
            r"[\W]", "", value.translate(
                maketrans("@ .-", "____")
            )
        ).lower()
    else:
        return ""



def format_formdata(**kwargs):

    form_template = kwargs["form_template"]
    request = kwargs["request"]
    results = kwargs["results"]

    fields = {}
    for k,v in results.items():
        fields.update({ k: v })

    data = {
        'fields': fields
    }

    if request.user.is_authenticated():
        data.update({
                "user": {
                    "username":     request.user.username,
                    "first_name":   request.user.first_name,
                    "last_name":    request.user.last_name,
                    "email":        request.user.email
                }
            })

    form_response =  FormData.objects.create(form_template=form_template, data=data)

    data.update({"schema": create_schema(form_response)})

    form_response.save()

    return form_response


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
