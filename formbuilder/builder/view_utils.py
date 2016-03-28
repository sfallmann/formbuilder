import requests
import json
from django.conf import settings
from django.http import HttpResponse


def ajax_response(code, data):

    context = {
        'status': code
    }

    context.update(**data)

    response = HttpResponse(json.dumps(context), content_type="application/json")

    response.status_code = code
    return response


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
