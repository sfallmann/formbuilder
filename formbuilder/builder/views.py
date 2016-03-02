import json
import collections
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from .models import FormTemplate, FormData
from .forms import Form



'''
Views for rendering forms, capturing submitted data,
and displaying the captured\saved results
'''

def formtemplate_results(request, id):
	'''
	formtemplate_results(request, id):

		View for displaying the saved form data FormData id.
	'''

	# Get the FormData object by id
	results = FormData.objects.get(id=id)

	return HttpResponse(json.dumps(results.data))



def formtemplate_details(request, id):
	'''
	formtemplate_details(request, id):

		View for displaying and capturing the form
		created from a FormTemplate.
	'''

	# Get the FormTemplate object by id
	template_ = FormTemplate.objects.get(id=id)

	# Pass the FormTemplate object into Form
	f = Form(obj=template_)


	if request.method == "POST":

		# Pass the FormTemplate object into Form with the posted data
		f = Form(template_, request.POST)

		# Check if the data is valid
		if f.is_valid():


			data = {
				"category": 	template_.category.name,
				"name": 		template_.name,
				"data":			f.cleaned_data
			}
			# Create the FormData object with the posted data
			results = FormData.objects.create(
				form_template=template_,
				data=data
			)

			# Redirect to view to display the save data
			return redirect(formtemplate_results, results.id)

	return render(request, 'builder/form.html', {"form": f},)


