import os
import json, re, requests
from collections import OrderedDict
from nested_dict import nested_dict
from django.conf import settings
from django.utils.html import mark_safe
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from crispy_forms.utils import render_crispy_form
from .models import FormTemplate, FormData, FieldTemplate, Category
from .forms import Form
from .formdata_utils import create_schema, prepare_files, format_folder_prefix
from .files import process_files, upload_ftp


from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit

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

    field_sets = results.data["schema"]["category"]["form_template"]["field_sets"]
    fields = results.data["fields"]

    data = json.dumps(results.data, sort_keys=True,
                 indent=4, separators=(',', ': '))

    '''
    if "files" in results.data:

        form.files = results.data["files"]

    form.use_as_prefix = format_directory_prefix(form.use_as_prefix)
    form_html = render_crispy_form(form, helper=form.helper, context=None)

    tform = Form(results.form_template)

    layout = tform.helper.layout
    for field in layout.fields:

        if field.__class__.__name__ == "Fieldset":
            if field.legend:
                print field.legend
            else:
                print "NO FIELDSET"

            for f in field:
                print f[0], results.data["data"][f[0]]


    msg_html = render_to_string('results.html', {'form': form })
    msg_plain = "plain message"

    send_mail(
        'Test Email',
        msg_plain,
        'sfallmann@pbmbrands.com',
        ['sfallmann@pbmbrands.com'],
        html_message=msg_html,
    )
    '''
    #return HttpResponse(json.dumps(results.data))
    return render(
        request, "results.html", {
            "field_sets": field_sets,
            "fields": fields,
            "data": data
        }
    )


@require_http_methods(["GET", "POST"])
def formtemplate_details(request, id):
    '''
    formtemplate_details(request, id):

        View for displaying and capturing the form
        created from a FormTemplate.
    '''

    #  Get the FormTemplate object by id
    form_template = FormTemplate.objects.get(id=id)

    #  Pass the FormTemplate object into Form
    form = Form(obj=form_template)

    if request.method == "POST":
        # Pass the FormTemplate object into Form with the posted data
        form = Form(form_template, request.POST, request.FILES)

            #  Check if the data is valid

        if form.is_valid():

            #  Create the FormData object with the posted data

            form_response = format_formdata(

                form_template=form_template,
                request=request,
                results=form.clean_data_only

            )
            files = prepare_files(request.FILES)

            print "form.use_as_prefix %s" % form.use_as_prefix

            process_files(
                files["prepped_files"],
                str(form_response.id),
                format_folder_prefix(form.use_as_prefix),
                ftp=True
            )
            #  Redirect to view to display the save data
            return redirect(formtemplate_results, form_response.id)

        else:

            return render(
                request, form.template, {
                    "form": form,
                    "header": mark_safe(form_template.header),
                    "footer": mark_safe(form_template.footer),
                }
            )

    return render(
        request, form.html_template, {
            "form": form,
            "header": mark_safe(form_template.header),
            "footer": mark_safe(form_template.footer),
        }
    )


@require_http_methods(["GET", "POST"])
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

    if request.method == "POST" and request.is_ajax():

        # Pass the FormTemplate object into Form with the posted data
        form = Form(form_template, request.POST, request.FILES)

        if form.is_valid():

            form_response = format_formdata(

                form_template=form_template,
                request=request,
                results=form.clean_data_only

            )

            files = prepare_files(request.FILES)

            print "form.use_as_prefix %s" % form.use_as_prefix

            process_files(
                files["prepped_files"],
                str(form_response.id),
                format_folder_prefix(form.use_as_prefix),
                ftp=True
            )

            json = {
                "message": "Submission was successful!",
                "redirect": form_response.get_absolute_url()
            }

            return ajax_response(200, json)

        else:

            data = {"message": "Form invalid. Refresh the page and try again."}

            return ajax_response(400, data)

    else:

        HttpResponse("Not an ajax request")


def format_formdata(**kwargs):

    form_template = kwargs["form_template"]
    request = kwargs["request"]
    results = kwargs["results"]

    fields = {}
    for k,v in results.items():
        fields.update({ k: v })

    data = {
        'fields': fields
    }

    if request.user.is_authenticated():
        data.update({
                "user": {
                    "username":     request.user.username,
                    "first_name":   request.user.first_name,
                    "last_name":    request.user.last_name,
                    "email":        request.user.email
                }
            })

    form_response =  FormData.objects.create(form_template=form_template, data=data)

    data.update({"schema": create_schema(form_response)})

    form_response.save()

    return form_response


@require_http_methods(["GET", "POST"])
def formresponse_query(request):

    categories = Category.objects.all()
    form_templates = FormTemplate.objects.all()

    if request.method == "GET":
        pass


    else:

        category_id = request.POST.get('category_id')
        formtemplate_id = request.POST.get('formtemplate_id')
        fieldname = request.POST.get('fieldname')
        value = request.POST.get('value')


        form_responses = FormData.objects.filter(
            form_template__category_id=int(category_id)
        )


        if formtemplate_id:
            form_responses.filter(form_template_id = int(formtemplate_id))


        fr_list = []

        for fr in form_responses:

            match_key = 0
            match_value = 0

            for fs_val in fr.data["field_sets"].values():

                for k,v in fs_val.items():

                    for _k,_v in v.items():
                        print _k, _v

        print category_id, formtemplate_id, fieldname_exact, value_exact, fieldname, value

    return render(
        request, "query.html", {
            "categories": categories,
            "form_templates": form_templates
        }
    )

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

    print ip

    recaptcha_response = request.POST["g-recaptcha-response"]

    print recaptcha_response

    url = 'https://www.google.com/recaptcha/api/siteverify'

    data = {
        "secret": secret,
        "remoteip": ip,
        "response": recaptcha_response
    }

    r = requests.post(url, data=data)
    print (r.text)
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
