from __future__ import unicode_literals
from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.core.urlresolvers import reverse
from django.core import serializers
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from helper.validators import is_alpha_num, is_alpha, is_alpha_num_words
from helper.serializers import get_json, get_dict
from helper.constants import input_types


class Category(models.Model):

	'''
	Category

	Category for your forms (Finance Department, Submissions, Contact, etc)

	'''

	name = models.CharField(max_length=50,unique=True)
	acronym = models.CharField(max_length=3,unique=True)
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
		max_length=30, validators=[is_alpha_num_words])
	category = models.ForeignKey(
		Category,
		related_name="form_templates",
	)
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
		return reverse(
			'builder.views.formtemplate_details',
			args=[str(self.category.acronym).lower(),str(self.id)])

	def as_dict(self):
		return get_dict(self)

	def as_json(self):
		return get_json(self)


class FormTemplateOptions(models.Model):

	'''
	FormTemplateOptions

	Options for a specific Form Template

	TODO: Add in the options!

	'''

	form_template = models.OneToOneField(
		FormTemplate,
		on_delete=models.CASCADE,
		primary_key=True
	)

	class Meta:
		verbose_name = "Options"
		verbose_name_plural = "Options"


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
	)
	name = models.CharField(
		max_length=30, validators=[is_alpha_num_words])

	class Meta:
		unique_together = (("name", "form_template"),)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = "Fieldset"
		verbose_name_plural = "Fieldsets"


class FieldTemplate(models.Model):

	'''
	FieldTemplate

	A template for a field added to specific FormTemplate.
	Can be part of a FormTemplate's FieldSet

	FIELD_TYPE_CHOICES = list of field types that can be selected.

	'''


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

	field_set = models.ForeignKey(
		FieldSet,
		related_name="field_templates",
		blank=True,
		null=True,
		on_delete=models.SET_NULL,
	)

	position = models.PositiveIntegerField(default=None,null=True, blank=True)

	class Meta:
		unique_together = (("name", "form_template"),)
		verbose_name = "Field Template"
		verbose_name_plural = "Field Templates"

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

	'''
	FieldTemplateOptions

	Options for a specific FieldTemplate.
	Encompasses all the values that can be set for rendering the field as html.

	'''

	field_template = models.OneToOneField(
		FieldTemplate,
		on_delete=models.CASCADE,
		primary_key=True
	)
	label = models.CharField(max_length=50, blank=True)

	# Common tag attributes
	autofocus = models.BooleanField(default=False)
	max_length = models.PositiveIntegerField(null=True, blank=True)
	placeholder = models.TextField(blank=True)
	read_only = models.BooleanField(default=False)
	required = models.BooleanField(default=True)

	# HTML Input tag attributes
	autocomplete = models.BooleanField(default=True)
	checked = models.BooleanField(default=False)
	disabled = models.BooleanField(default=False)
	min_length = models.PositiveIntegerField(null=True, blank=True)
	min_value = models.IntegerField(null=True, blank=True)
	max_value = models.IntegerField(null=True, blank=True)
	pattern = models.CharField(max_length=50, blank=True, default="")

	# HTML Textarea tag attributes
	columns = models.PositiveIntegerField(null=True, blank=True)
	rows = models.PositiveIntegerField(null=True, blank=True)

	# HTML for implementing tags with choices
	choices = ArrayField(
		models.CharField(max_length=30, blank=True),
		null=True
	)

	class Meta:
		verbose_name = "Options"
		verbose_name_plural = ""

	def __str__(self):
		return ""


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

	class Meta:
		verbose_name = "Form Response"
		verbose_name_plural = "Form Responses"

	def __str__(self):
		return "%s Response: %s" % (
			self.form_template.name, self.created.strftime("%A, %d. %B %Y %I:%M%p"))

	def get_absolute_url(self):
		return reverse(
			'builder.views.formtemplate_results',
			args=[str(self.form_template.category.acronym).lower(),str(self.id)])



