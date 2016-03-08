from django.contrib import admin
from django.conf import settings
from django.utils.html import mark_safe
from django import forms
from django.db import models
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from .models import Category
from .models import FormData, FormTemplate, FieldSet
from .models import FieldTemplate, FieldChoice
from .adminforms import FieldTemplateInlineForm, FieldTemplateForm
from .adminforms import FieldSetInlineForm, FormTemplateForm
from ckeditor.widgets import CKEditorWidget
from helper.constants import field_types




class CategoryAdmin(admin.ModelAdmin):

	prepopulated_fields = {"slug": ("name",)}


class FieldTemplateInline(admin.StackedInline):
	model = FieldTemplate
	form = FieldTemplateInlineForm
	show_change_link = True
	extra = 0

	def get_formset(self, request, obj, **kwargs):

		self.fields = ["name","form_template","field_type","field_set","label","position",]

		return super(FieldTemplateInline, self).get_formset(request, obj, **kwargs)

	def get_queryset(self, request):
			return super(FieldTemplateInline, self).get_queryset(request).order_by('field_set','position')

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "field_set":
			try:
				parent_obj_id = request.resolver_match.args[0]
				form_template = FormTemplate.objects.get(id=parent_obj_id)
				kwargs["queryset"] = FieldSet.objects.filter(form_template=form_template)
			except IndexError:
				kwargs["queryset"] = FieldSet.objects.none()

		return super(FieldTemplateInline, self).formfield_for_foreignkey(
			db_field, request, **kwargs)

class FieldChoiceInline(admin.StackedInline):
	model = FieldChoice
	extra = 1


class FieldTemplateAdmin(admin.ModelAdmin):

	form = FieldTemplateForm
	list_display = ('name', 'field_type', 'form_template','field_set','position')
	ordering = ('field_set','form_template', 'position', 'field_type','name')
	list_filter = ('form_template','field_set',)


	def get_form(self, request, obj, **kwargs):

		self.fields = ["name","form_template","field_type","field_set","label","position",]

		if obj:
			common = ["form_template","field_set","field_type","name","label","position",]
			field_types.ATTRS[obj.field_type].sort()
			self.fields = common + field_types.ATTRS[obj.field_type]

			if obj.field_type == "select" or obj.field_type == "radio":
				self.inlines =[FieldChoiceInline,]

		return super(FieldTemplateAdmin, self).get_form(request, obj, **kwargs)



class FieldSetAdmin(admin.ModelAdmin):
	pass


class FieldSetFormSet(BaseInlineFormSet):

	def clean(self):
		super(FieldSetFormSet, self).clean()

		for form in self.forms:
			if not hasattr(form, 'cleaned_data'):
				continue

			if form.instance.name == settings.EMPTY_FIELDSET:
				data = form.cleaned_data

				if(data.get('name') != settings.EMPTY_FIELDSET):
					raise ValidationError(
						'FieldSet %s cannot be renamed!' % settings.EMPTY_FIELDSET)

				if (data.get('DELETE')):
					raise ValidationError(
						'FieldSet %s can never be deleted!' % settings.EMPTY_FIELDSET)


class FieldSetInline(admin.StackedInline):

	model = FieldSet
	form = FieldSetInlineForm
	formset = FieldSetFormSet
	show_change_link = False

	extra = 0

	fieldsets = (
		(None, {
			'fields': ('name', 'label')
		}),
		('Advanced options', {
			'classes': ('collapse',),
			'fields': ('helper_text',),
		}),
	)
	def get_formset(self, request, obj, **kwargs):

		return super(FieldSetInline, self).get_formset(request, obj, **kwargs)

class FormTemplateAdmin(admin.ModelAdmin):
	form = FormTemplateForm
	inlines = [FieldSetInline, FieldTemplateInline,]

	fieldsets = (
		(None, {
			'fields': ('name', 'category', 'login_required', 'notification_list')
		}),
		('Advanced options', {
			'classes': ('collapse',),
			'fields': ('header','footer'),
		}),
	)


class FormDataAdmin(admin.ModelAdmin):
	list_display = ("__str__","form_template", "data_category")
	ordering = ('form_template', 'id')
	readonly_fields = ["form_template", "data"]

	def data_category(self, obj):

		if obj.form_template:
			return obj.form_template.category
		else:
			return None

	data_category.short_description = "Category"


admin.site.register(Category, CategoryAdmin)
admin.site.register(FieldTemplate, FieldTemplateAdmin)
#admin.site.register(FieldSet, FieldSetAdmin)
admin.site.register(FormTemplate, FormTemplateAdmin)
admin.site.register(FormData, FormDataAdmin)
