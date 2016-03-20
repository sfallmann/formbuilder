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
        # Pass the FormTemplate object into Form with the posted data
        f = Form(template_, request.POST, request.FILES)

        recaptcha_passed = recaptcha_check(request)

        if not recaptcha_passed:

            recaptcha_error = "<hr/><h4 class='alert alert-danger'>%s</h4>"\
                % 'reCAPTCHA failed. Please try again.'

            return render(
                request, f.html_template, {
                    "form": f,
                    "header": mark_safe(template_.header),
                    "footer": mark_safe(template_.footer),
                    "recaptcha_error": recaptcha_error,
                }
            )

        else:

            #  Check if the data is valid

            if f.is_valid():

                #  Create the FormData object with the posted data
                formdata = create_formdata(
                    template_, f.clean_data_only, request.user)

                uploaded_file_list = []

                for rf in request.FILES:

                    file_list = request.FILES.getlist(rf)

                    for file_ in file_list:
                        uploaded_file_list.append(file_.name)

                        if settings.DEBUG == True:
                            handle_uploaded_file(file_, str(formdata.pk))

                    formdata.data.update({
                            "files": uploaded_file_list
                        })

                    formdata.save()

                #  Redirect to view to display the save data
                return redirect(formtemplate_results, formdata.id)

            else:

                return render(
                    request, f.template, {
                        "form": f,
                        "header": mark_safe(template_.header),
                        "footer": mark_safe(template_.footer),
                    }
                )

    return render(
        request, f.html_template, {
            "form": f,
            "header": mark_safe(template_.header),
            "footer": mark_safe(template_.footer),
        }
    )



def formtemplate_details_ajax(request, id):
    '''
    formtemplate_details(request, id):

        View for displaying and capturing the form
        created from a FormTemplate.
    '''

    #  Get the FormTemplate object by id
    form_template = FormTemplate.objects.get(id=id)

    #  Pass the FormTemplate object into Form
    form = Form(obj=form_template)

    if request.method == "GET":

        return render(
            request, form.html_template, {
                "form": form,
                "header": mark_safe(form_template.header),
                "footer": mark_safe(form_template.footer),
            }
        )

    if request.method == "POST":

        if request.is_ajax():

            # Pass the FormTemplate object into Form with the posted data
            form = Form(form_template, request.POST, request.FILES)

            if form.is_valid():

                uploaded_file_list = []

                #  Create the FormData object with the posted data
                formdata = create_formdata(
                   form_template, form.clean_data_only, request.user)

                for file_list in request.FILES:

                    files = request.FILES.getlist(file_list)

                    for f in files:

                        uploaded_file_list.append(f.name)

                        if settings.DEBUG == False:
                            transfer_success = handle_uploaded_file(f, str(formdata.pk))

                    formdata.data.update({
                            "files": uploaded_file_list
                        })

                    formdata.save()

                data = {
                    "message": "Submission was successful!",
                    "redirect": formdata.get_absolute_url()
                }

                return ajax_response(200, data)

            else:

                data = {"message": "Form invalid. Refresh the page and try again."}

                return ajax_response(400, data)

            '''
                if not f.is_valid():





                    uploaded_file_list = []

                    for rf in request.FILES:

                        file_list = request.FILES.getlist(rf)

                        for file_ in file_list:
                            uploaded_file_list.append(file_.name)

                            if settings.DEBUG == True:
                                handle_uploaded_file(file_, str(formdata.pk))

                        formdata.data.update({
                                "files": uploaded_file_list
                            })

                        formdata.save()

                    #  Redirect to view to display the save data
                    return redirect(formtemplate_results, formdata.id)

                else:

                    return render(
                        request, f.template, {
                            "form": f,
                            "header": mark_safe(template_.header),
                            "footer": mark_safe(template_.footer),
                        }
                    )
            '''
        else:

            HttpRepsone("Not an ajax request")



def ajax_response(code, data):

    context = {
        'status': code
    }

    context.update(**data)

    response = HttpResponse(json.dumps(context), content_type="application/json")

    response.status_code = code
    return response



def handle_uploaded_file(f, folder):

    path = os.path.join(UPLOAD_FOLDER, ("%s/" % folder))

    new_folder = make_folder(path)

    if new_folder:

        filepath = os.path.join(path, f._name)

        try:
            with open(filepath, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)

        except:
            #TODO logging and specific exceptions
            return False


def make_folder(folder):

    if not os.path.exists(folder):
        try:
            os.makedirs(folder)

        except OSError:

            #  TODO:  Add logging
            #  "Error on creating file folder"
            return False

    return True

def recaptcha_check_ajax(request):

    secret = settings.RECAPTCHA_SECRET
    ip = get_client_ip(request)

    recaptcha_response = request.POST["g-recaptcha-response"]
    url = 'https://www.google.com/recaptcha/api/siteverify'

    data = {
        "secret": secret,
        "remoteip": ip,
        "response": recaptcha_response
    }

    r = requests.post(url, data=data)

    response = HttpResponse(r, content_type="application/json")

    return response

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
