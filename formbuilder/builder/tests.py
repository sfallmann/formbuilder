from django.test import TestCase
from django.core import serializers
from .models import Department
from .models import FormTemplate, FieldTemplate, FieldTemplateOptions


class FormTemplateTestCase(TestCase):
    def setUp(self):
        fin = Department.objects.create(
            name="Finance",
            acronym="FIN"
        )
        form = FormTemplate.objects.create(
            name="TestForm",
            department=fin
        )
        field = FieldTemplate.objects.create(
            name="email",
            form_template=form
        )
        options = FieldTemplateOptions.objects.create(
            field_template=field
        )

    def test_as_dict(self):
        fin = Department.objects.get(name="Finance")
        form = FormTemplate.objects.get(name="TestForm", department=fin)
        field = FieldTemplate.objects.get(name="email", form_template=form)
        options = FieldTemplateOptions.objects.get(field_template=field)

        print form.as_dict()
        print form.get_absolute_url()
        #print form.as_json()
