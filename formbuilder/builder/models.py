from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField, ArrayField
from django.core.urlresolvers import reverse
from django.core import serializers
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.conf import settings
from colorful.fields import RGBColorField
from helper.validators import is_lower, min_20, max_files
from helper.validators import is_alpha_num, is_alpha, is_alpha_num_words
from helper.validators import is_alpha_num_whitespace, is_alpha_num_nospace
from helper.serializers import get_json, get_dict
from helper.constants import field_types


class DictBase(models.Model):

    key = models.CharField(
        max_length=32, validators=[is_alpha_num_words, is_lower]
    )
    value = models.CharField(max_length=255)

    class Meta:
        abstract = True


class Category(models.Model):

    '''
    Category

    Category for your forms (Finance Department, Submissions, Contact, etc)

    '''

    name = models.CharField(max_length=50, unique=True)
    acronym = models.CharField(max_length=3, unique=True)
    slug = models.SlugField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class FormTemplate(models.Model):

    '''
    FormTemplate

    Template for the user created form.

    Methods:


        get_json(self):
            returns json serialization of the instance

        get_formfields(self):
            returns all related FieldTemplate objects
    '''

    name = models.CharField(
        max_length=30,
        validators=[is_alpha_num_words]
    )

    category = models.ForeignKey(
        Category,
        related_name="form_templates",
    )

    login_required = models.BooleanField(
        default=False,
        help_text="Not fully implemented yet"

    )

    notification_list = ArrayField(
        models.EmailField(max_length=100, blank=True),
        help_text="List of comma seperated email addresses that will be sent"\
            " a notification when the form has been submitted"
    )

    dropzone = models.BooleanField(
        default=False,
        help_text="A dropzone is an area on the form where files can be dropped for upload"
    )
    background_color = RGBColorField(default="#FFFFFF")
    text_color = RGBColorField(default="#000000")

    header = models.TextField(blank=True)
    footer = models.TextField(blank=True)

    published = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("name", "category"),)
        verbose_name = "Form Template"
        verbose_name_plural = "Form Templates"

    def __str__(self):
        return self.name

    def get_absolute_url(self):

        if self.dropzone:
            return reverse(
                'formtemplate_details_ajax',
                args=[str(self.id)])
        else:
            return reverse(
                'formtemplate_details',
                args=[str(self.id)])

    def get_admin_change_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse(
            "admin:%s_%s_change" % (
                content_type.app_label, content_type.model), args=(self.id,))

    def as_dict(self):
        return get_dict(self)

    def as_json(self):
        return get_json(self)


class FieldSet(models.Model):

    '''
    FieldSet

    FieldSet for a specific Form Template.
    FieldTemplate's can be assigned to a FieldSet

    '''

    form_template = models.ForeignKey(
        FormTemplate,
        related_name="fieldsets",
        on_delete=models.CASCADE,
        editable=False
    )
    name = models.CharField(
        max_length=30, validators=[is_alpha_num_nospace, is_lower])
    label = models.CharField(
        max_length=100, blank=True,
        help_text="defines a caption for the fieldset element; "\
            "represents the legend html tag"
    )
    position = models.PositiveIntegerField(default=None, null=True, blank=True)
    accordion = models.BooleanField(default=False)

    class Meta:
        unique_together = (("name", "form_template"),)
        verbose_name = "Fieldset"
        verbose_name_plural = "Fieldsets"

    def __str__(self):
        return "%s: %s" % (self.name, self.form_template.name)


class FieldTemplate(models.Model):

    '''
    FieldTemplate

    A template for a field added to specific FormTemplate.
    Can be part of a FormTemplate's FieldSet

    FIELD_TYPE_CHOICES = list of field types that can be selected.

    '''

    CSS_STRING = "col-sm-%s"

    FIELD_TYPE_CHOICES = (
        [
            (v, v) for v in field_types.as_list()
        ]
    )

    CSS_CLASS_CHOICES = (
        [
            (CSS_STRING % x, CSS_STRING % x) for x in xrange(1,13)
        ]
    )

    name = models.CharField(
        max_length=30, validators=[is_alpha_num_whitespace, is_lower])
    form_template = models.ForeignKey(
        FormTemplate,
        related_name="field_templates",
        on_delete=models.CASCADE,
        editable=False
    )
    field_type = models.CharField(
        max_length=20, choices=FIELD_TYPE_CHOICES, default=field_types.TEXT)

    field_set = models.ForeignKey(
        FieldSet,
        related_name="field_templates",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    position = models.PositiveIntegerField(default=None, null=True, blank=True)
    css_class = models.CharField(
        max_length=20, choices=CSS_CLASS_CHOICES, default="col-sm-12")


    label = models.CharField(max_length=50, blank=True)
    use_as_prefix = models.BooleanField(
        default=False,
        help_text="The value of this field will be added as a prefix to"\
            "file and folder names."
    )
    send_confirmation = models.BooleanField(default=False)
    help_text = models.CharField(max_length=500, blank=True)
    # Common tag attributes
    autofocus = models.BooleanField(default=False)
    maxlength = models.PositiveIntegerField(
        null=True, blank=True, default=100, validators=[min_20, ])
    placeholder = models.TextField(blank=True)
    readonly = models.BooleanField(default=False)
    required = models.BooleanField(default=False)

    # HTML Input tag attributes
    autocomplete = models.BooleanField(default=True)
    checked = models.BooleanField(default=False)
    disabled = models.BooleanField(default=False)
    minlength = models.PositiveIntegerField(null=True, blank=True)
    minvalue = models.IntegerField(null=True, blank=True)
    maxvalue = models.IntegerField(null=True, blank=True)
    pattern = models.CharField(max_length=50, blank=True, default="")

    # HTML Textarea tag attributes
    cols = models.PositiveIntegerField(null=True, blank=True)
    rows = models.PositiveIntegerField(null=True, blank=True, default=6)

    html = models.TextField(blank=True)

    maxfiles = models.IntegerField(
        null=True, blank=True, validators=[max_files, ], default=1)
    accept = ArrayField(
        models.CharField(max_length=10, blank=True), null=True, blank=True
    )

    class Meta:
        unique_together = (("name", "form_template"),)
        verbose_name = "Field Template"
        verbose_name_plural = "Field Templates"

    def __str__(self):
        return self.name

    def get_form_admin_change_url(self):


        content_type = ContentType.objects.get_for_model(
            self.form_template.__class__
        )
        return reverse(
            "admin:%s_%s_change" % (
                content_type.app_label, content_type.model), args=(
                self.form_template.id,)
        )

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


class FieldChoice(DictBase):


    class Meta:
        unique_together = [('key', 'field_template'),('value', 'field_template')]

    field_template = models.ForeignKey(
        FieldTemplate,
        related_name="field_choices",
        on_delete=models.CASCADE,
    )



    def __str__(self):
        return "Field: %s  [key:%s], [value:%s]" % (
            self.field_template.name, self.key, self.value)


class DataManager(models.Manager):

    def search_fields(self, **kwargs):

        qs = super(DataManager, self).get_queryset().all()

        if kwargs.has_key("key_value_pair"):

            key = kwargs["key_value_pair"][0].lower()
            value = kwargs["key_value_pair"][1].lower()

            found_match = 0

            for q in qs:

                for k, v in q.data["fields"].items():

                    if key in k.lower() and value in str(v).lower():
                        found_match = 1
                        break

                if not found_match:

                    qs = qs.exclude(id=q.id)

        if kwargs.has_key("key_and_value"):

            key = kwargs["key_and_value"][0].lower()
            value = kwargs["key_and_value"][1].lower()

            found_key = 0
            found_value = 0

            for q in qs:

                for k,v in q.data["fields"].items():
                    if key in k.lower():
                        found_key = 1

                    if value in str(v).lower():
                        found_value = 1

                    if found_key and found_value:
                        break

                if not found_key and not found_value:

                    qs = qs.exclude(id=q.id)

        if kwargs.has_key("key_or_value"):

            key = kwargs["key_or_value"][0].lower()
            value = kwargs["key_or_value"][1].lower()

            found_key = 0
            found_value = 0

            for q in qs:

                print q

                for k,v in q.data["fields"].items():

                    if key in k.lower():
                        found_key = 1

                    if value in str(v).lower():
                        found_value = 1

                    if found_key or found_value:
                        break

                if not found_key or not found_value:

                    qs = qs.exclude(id=q.id)

        if kwargs.has_key("key"):

            key = kwargs["key"].lower()

            found_key = 0

            for q in qs:

                for k in q.data["fields"].keys():

                    if key in k.lower():
                        found_key = 1
                        break

                if not found_key:


                    qs = qs.exclude(pk=q.pk)


        if kwargs.has_key("value"):

            value = kwargs["value"].lower()

            found_value = 0

            for q in qs:

                for v in q.data["fields"].values():
                    if value in str(v).lower():
                        found_value = 1
                        break

                if not found_value:

                    qs = qs.exclude(id=q.id)

        return qs


class FormData(models.Model):

    '''
    FormData

    The data collected from an html rendered FormTemplate

    '''

    form_template = models.ForeignKey(
        FormTemplate,
        related_name="form_data",
        null=True,
        on_delete=models.SET_NULL
    )

    data = JSONField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    data_objects = DataManager()

    class Meta:
        verbose_name = "Form Response"
        verbose_name_plural = "Form Responses"

    def __str__(self):
        tzadjusted_created = timezone.localtime(self.created)
        return "Response: [id:%s]  %s" % (
            self.pk, tzadjusted_created.strftime("%A, %d. %B %Y %I:%M%p"))

    def get_absolute_url(self):
        return reverse(
            'builder.views.formtemplate_results',
            args=[str(self.id)])

    def key_in_data_fields(self, string):

        fields = self.data["fields"]

        for k in fields.keys():
            if string in k:
                return True

        return False

    def value_in_data_fields(self, string):

        fields = self.data["fields"]

        for v in fields.values():
            if string in v:
                return True

        return False




