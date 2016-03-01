import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from .models import FormTemplate, FormData
from .forms import Form


def myotherfunction():
    logger.error("this is an error message!!")


def formtemplate_results(request, id):

    results = FormData.objects.get(id=id)

    return HttpResponse(json.dumps(results.data))


def formtemplate_details(request, id):
    _form = FormTemplate.objects.get(id=id)

    f = Form(obj=_form)

    if request.method == "POST":

        f=Form(_form, request.POST)

        if f.is_valid():

            results = FormData.objects.create(form_template=_form,data=f.cleaned_data)

            return redirect(formtemplate_results, results.id)

    return render(request, 'builder/form.html', {"form": f},)


