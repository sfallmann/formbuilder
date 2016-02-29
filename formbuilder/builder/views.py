from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import json
from .models import FormTemplate, FormData
from .forms import Form


def json_formtemplate(request, id):
    _form = FormTemplate.objects.get(id=id)

    f = Form(obj=_form)

    if request.method == "POST":
        f=Form(_form, request.POST)
        if f.is_valid():

            _data = FormData.objects.create(form_template=_form,data=f.cleaned_data)

            print _data.data
        else:
            print "\n Not valid! \n"

    elif request.method == "GET":
        pass

    return render(request, 'builder/form.html', {"form": f},)
