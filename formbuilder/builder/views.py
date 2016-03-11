import os
import json
import requests
import collections
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from .models import FormTemplate, FormData
from .forms import Form
from django.conf import settings
from django.utils.html import mark_safe

FILESTORE = FileSystemStorage(location='/uploads')
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

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

    #  Get the FormTemplate object by id
    template_ = FormTemplate.objects.get(id=id)

    #  Pass the FormTemplate object into Form
    f = Form(obj=template_)

    if request.method == "POST":

        recaptcha_passed = recaptcha_check(request)

        # Pass the FormTemplate object into Form with the posted data
        f = Form(template_, request.POST, request.FILES)

        #  Check if the data is valid

        print "Got the files I think: %s" % request.FILES

        if f.is_valid():  # and recaptcha_passed:


            print f.cleaned_data
            print request.FILES

            #  Create the FormData object with the posted data
            formdata = create_formdata(
                template_, f.clean_data_only, request.user)

            for file_ in f.file_list:
                handle_uploaded_file(file_, str(formdata.pk))

            #  Redirect to view to display the save data
            return redirect(formtemplate_results, formdata.id)

        else:

            recaptcha_error = "<p class='alert alert-danger'>%s</h4>"\
                % 'reCAPTCHA failed. Please try again.'

            return render(
                request, 'builder/form.html', {
                    "form": f,
                    "header": mark_safe(template_.header),
                    "recaptcha_error": recaptcha_error
                }
            )

    return render(
        request, 'form.html', {
            "form": f,
            "header": mark_safe(template_.header)
        }
    )


def handle_uploaded_file(f, folder):

    path = os.path.join(UPLOAD_FOLDER, ("%s/" % folder))

    make_folder(path)

    filepath = os.path.join(path, f._name)

    with open(filepath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def make_folder(folder):

    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except OSError:
            error = "Error on creating file folder"


def recaptcha_check(request):

    secret = settings.RECAPTCHA_SECRET
    ip = get_client_ip(request)

    response = request.POST["g-recaptcha-response"]
    url = 'https://www.google.com/recaptcha/api/siteverify'

    data = {
        "secret": secret,
        "remoteip": ip,
        "response": response
    }

    r = requests.post(url, data=data)
    r_json = json.loads(r.text)

    return r_json["success"]


def get_client_ip(request):

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_formdata(form, results, user):

    data = {
        "category": 	form.category.name,
        "name": 		form.name,
        "data":			results,
    }

    if user.is_authenticated():
        data.update({
                "user": {
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email
                }
            })

    return FormData.objects.create(form_template=form, data=data)
