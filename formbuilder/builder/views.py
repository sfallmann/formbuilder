import json
from crispy_forms.utils import render_crispy_form
from django.conf import settings

#  May not need-depends on formtemplate_results.
from django.utils.html import mark_safe
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
#
from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from .models import FormTemplate, FormData, FieldTemplate, Category
from .forms import Form
from .formdata_utils import prepare_files
from .formdata_utils import format_folder_prefix, format_formdata
from .view_utils import recaptcha_check_ajax, ajax_response
from .files import FileProcessor
#from .files import process_files, upload_ftp, FileProcessor

'''
Views for rendering forms, capturing submitted data,
and displaying the captured\saved results
'''


def category_menu(request):

    categories = Category.objects.all()

    return render(
        request, "menu.html", {
            "categories": categories
        }
    )

@xframe_options_exempt
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
    form.use_as_prefix = format_directory_prefix(form.use_as_prefix)
    form_html = render_crispy_form(form, helper=form.helper, context=None)



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

@xframe_options_exempt
@require_http_methods(["GET", "POST"])
def formtemplate_details(request, category, slug):
    '''
    formtemplate_details(request, slug):

        View for displaying and capturing the form
        created from a FormTemplate.
    '''

    #  Get the FormTemplate object by id
    form_template = FormTemplate.objects.get(category__slug=category, slug=slug)

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


            if files["prepped_files"]:
                fp = FileProcessor(
                    str(form_response.id),
                    format_folder_prefix(form.use_as_prefix),
                    True
                )

                fp.process_files(files["prepped_files"])

            if request.is_ajax():

                json = {
                    "message": "Submission was successful!",
                    "redirect": form_response.get_absolute_url()
                }

                return ajax_response(200, json)

            else:

                #  Redirect to view to display the save data
                return redirect(formtemplate_results, form_response.id)

        else:

            if request.is_ajax():

                data = {"message": "Form invalid. Refresh the page and try again."}
                return ajax_response(400, data)

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
