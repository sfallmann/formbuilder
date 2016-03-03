from django import forms
from .models import FieldTemplate


class FieldTemplateInlineForm(forms.ModelForm):


	def __init__(self, *args, **kwargs):

		super(FieldTemplateInlineForm, self).__init__(*args, **kwargs)

		if "instance" in kwargs:
			f = kwargs["instance"]
			fields = FieldTemplate.objects.filter(
				form_template=f.form_template, field_set=f.field_set)
			count = fields.count()
			value = f.position

			choices = ([(x, x) for x in range(1, count+1)])

			self.fields['position'] = forms.ChoiceField(choices=(choices), required=False, initial=value)
			self.fields['position'].show_hidden_initial = True
		else:
			self.fields['position'].disabled = True

class FieldTemplateForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):

		super(FieldTemplateForm, self).__init__(*args, **kwargs)

		instance = kwargs.get('instance')


		if instance:

			fields = FieldTemplate.objects.filter(
				form_template=instance.form_template,
				field_set=instance.field_set
			)

			count = fields.count()

			position_choices = ([(x, x) for x in range(1, count+1)])

			self.fields['position'] = forms.ChoiceField(choices=position_choices, required=False)
			self.fields['field_set'].queryset = FieldSet.objects.filter(
				form_template=instance.form_template)
		else:

			form_template = None
			fields = FieldTemplate.objects.filter(field_set=None)
			count = fields.count() + 1

			self.fields['position'].disabled = True
