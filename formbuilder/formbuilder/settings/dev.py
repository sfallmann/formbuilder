from base import *

INSTALLED_APPS += ['debug_toolbar',]

DEBUG = True
#DEBUG_TOOLBAR_PATCH_SETTINGS = False

def show_toolbar(request):
    return False

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK" : show_toolbar,
}


INTERNAL_IPS = [
    '127.0.0.1:8000',
    'localhost:8000',
    '192.168.1.6:8000',
]
ALLOWED_HOSTS = ["*"]
