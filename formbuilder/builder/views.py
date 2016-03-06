import os
import json
import collections
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from .models import FormTemplate, FormData
from .forms import Form
from django.conf import settings



FILESTORE = FileSystemStorage(location='/uploads')
UPLOAD_FOLDER = os.getcwd() +"/uploads"


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
        f = Form(template_, request.POST, request.FILES)

        print f.files
        print f.changed_data

        # Check if the data is valid
        if f.is_valid():

            data = {
                "category": 	template_.category.name,
                "name": 		template_.name,
                "data":			f.clean_data_only
            }
            # Create the FormData object with the posted data
            results = FormData.objects.create(
                form_template=template_,
                data=data
            )



            for file_ in f.file_list:
                handle_uploaded_file(file_, str(results.pk))

            # Redirect to view to display the save data
            return redirect(formtemplate_results, results.id)

    return render(request, 'builder/form.html', {"form": f},)


def handle_uploaded_file(f, folder):

    path = UPLOAD_FOLDER + "/%s/" % (folder)

    make_folder(path)

    filepath = path + "/" + str(f._name)

    with open(filepath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def make_folder(folder):

    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except OSError:
            error = "Error on creating file folder"


