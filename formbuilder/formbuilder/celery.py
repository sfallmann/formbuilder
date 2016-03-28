from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "formbuilder.settings.dev")
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "formbuilder.settings.prod")


app = Celery("formbuilder", backend='rpc://', broker='amqp://')
