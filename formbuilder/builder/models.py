<<<<<<< HEAD
"""Builder app models"""
from __future__ import unicode_literals
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.core import serializers
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from helper.validators import is_alpha_num, is_alpha, is_alpha_num_words
from helper.serializers import get_json, get_dict
from helper.constants import input_types
# Constants



class Department(models.Model):

    '''
    Department Model-
        Company division or department.

        Attributes-

            name:       Name of the department.
                        CharField - must be unique, max length 50
            acronym:    Acronym of the department.
                        CharField - must be unique, max length 3
            slug:       Slugified name.
                        Prepopulated in the admin view for this model.
                        SlugField - max length 100
            created:    Date and time the instance was created.
                        DateTimeField
            modified:   Date and time the instance was last changed.
                        DateTimeField
    '''

    name = models.CharField(max_length=50,unique=True)
    acronym = models.CharField(max_length=3,unique=True)
    slug = models.SlugField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class FormTemplate(models.Model):

    '''
    FormTemplate Model-
        Template for the user created form.

        Attributes-

            name:           Name of the form.
                            CharField - must be unique, max length 30
            department:     Department the instance will belong to.
                            ForeignKey - Department,
                                         related_name="form_templates",
                                         related_query_name="form_template",
                                         null=True
            published:      Check when the form should be usable
                            BooleanField - default=False
            created:        Date and time the instance was created.
                            DateTimeField
            modified:       Date and time the instance was last changed.
                            DateTimeField


        Methods:

            __str__(self):
                returns the instance name

            get_json(self):
                returns json serialization of the instance

            get_formfields(self):
                returns all related FieldTemplate objects


    '''

    name = models.CharField(
        max_length=30, validators=[is_alpha_num_words])
    department = models.ForeignKey(
        Department,
        related_name="form_templates",
    )
    published = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("name", "department"),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('builder.views.json_formtemplate', args=[str(self.id)])

    def as_dict(self):
        return get_dict(self)

    def as_json(self):
        return get_json(self)


class FormTemplateOptions(models.Model):
    form_template = models.OneToOneField(
        FormTemplate,
        on_delete=models.CASCADE,
        primary_key=True
    )


class FormSet(models.Model):
    form_template = models.ForeignKey(
        FormTemplate,
        related_name="formsets",
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=30, validators=[is_alpha_num])

    class Meta:
        unique_together = (("name", "form_template"),)

    def __str__(self):
        return self.name

class FieldTemplate(models.Model):

    FIELD_TYPE_CHOICES = (
        [
            (v, v) for v in input_types.as_list()
        ]
    )

    name = models.CharField(
        max_length=30, validators=[is_alpha_num])
    form_template = models.ForeignKey(
        FormTemplate,
        related_name="field_templates",
        on_delete=models.CASCADE,
    )
    field_type = models.CharField(
        max_length=20, choices=FIELD_TYPE_CHOICES, default=input_types.TEXT)
    max_length = models.PositiveIntegerField(default=20, null=True)

    class Meta:
        unique_together = (("name", "form_template"),)

    def __str__(self):
        return self.name

    def get_admin_change_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse(
            "admin:%s_%s_change" % (
                content_type.app_label, content_type.model), args=(self.id,))

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse(
            "admin:%s_%s_change" % (
                content_type.app_label, content_type.model), args=(self.id,))

    def as_dict(self):
        return get_dict(self)

    def as_json(self):
        return get_json(self)

class FieldTemplateOptions(models.Model):
    field_template = models.OneToOneField(
        FieldTemplate,
        on_delete=models.CASCADE,
        primary_key=True
    )
    label = models.CharField(
        max_length=50,
        blank=True,
    )
    formset = models.ForeignKey(
        FormSet,
        related_name="field_template_options",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    autocomplete = models.BooleanField(default=True)
    placeholder = models.TextField(blank=True)

    class Meta:
        verbose_name = ""
        verbose_name_plural = "Options"

    def __str__(self):
        return ""


class FormData(models.Model):

    form_template = models.ForeignKey(
        FormTemplate,
        related_name="form_data",
        null=True,
        on_delete=models.SET_NULL
    )
    data = JSONField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
=======
from __future__ import unicode_literals

from django.db import models

# Create your models here.
>>>>>>> fa07aeb8f3c6cab5dbbed23d5eedf386894d07ab
