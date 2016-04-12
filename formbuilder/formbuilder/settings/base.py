"""
Django settings for formbuilder project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import json
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRETS = os.path.join(BASE_DIR, 'secrets.json')
SECRET_KEY = json.loads(
    open(SECRETS, 'r').read())['DJANGO_SECRET_KEY']
RECAPTCHA_SECRET = json.loads(
    open(SECRETS, 'r').read())['RECAPTCHA_SECRET']
RECAPTCHA_SITEKEY = json.loads(
    open(SECRETS, 'r').read())['RECAPTCHA_SITEKEY']

COUNTRIES_JSONFILE = os.path.join(BASE_DIR, 'countries.json')
COUNTRIES_LIST = json.loads(
    open(COUNTRIES_JSONFILE, 'r').read())['COUNTRIES']

COUNTRIES_TUPLES = [(c,c) for c in COUNTRIES_LIST]

EMAIL_HOST = json.loads(
    open(SECRETS, 'r').read())['EMAIL_HOST']
EMAIL_HOST_USER = json.loads(
    open(SECRETS, 'r').read())['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = json.loads(
    open(SECRETS, 'r').read())['EMAIL_HOST_PASSWORD']
EMAIL_PORT = 587
EMAIL_USE_TLS = True

FTP_SERVER = json.loads(
    open(SECRETS, 'r').read())['FTP_SERVER']
FTP_USERNAME = json.loads(
    open(SECRETS, 'r').read())['FTP_USERNAME']
FTP_PASSWORD = json.loads(
    open(SECRETS, 'r').read())['FTP_PASSWORD']


DEFAULT_FROM_EMAIL = "sfallmann@pbmbrands.com"


# Application definition

INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'builder.apps.BuilderConfig',
    'login.apps.LoginConfig',
    'crispy_forms',
    'floppyforms',
    'ckeditor',
    'ckeditor_uploader',
    'social.apps.django_app.default',
    'djangobower',
    'guardian',
    'nested_inline',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'formbuilder.urls'

PROJECT_TEMPLATES = BASE_DIR + "/templates"

WSGI_APPLICATION = 'formbuilder.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [

        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
            ],
        },
    },
]

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'formbuilder_dev',
        # The following settings are not used with sqlite3:
        'USER': 'form_dev',
        'PASSWORD': '$Password1',
        'HOST': 'localhost',                      # Empty for localhost through domain sockets or           '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}


AUTHENTICATION_BACKENDS = (
'django.contrib.auth.backends.ModelBackend',
'social.backends.facebook.FacebookOAuth2',
'social.backends.google.GoogleOAuth2',
'social.backends.twitter.TwitterOAuth',
'social.backends.amazon.AmazonOAuth2',
'guardian.backends.ObjectPermissionBackend',
)

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

#SESSION_SERIALIZER='django.contrib.sessions.serializers.PickleSerializer'

### Python Social Auth ###
# Facebook settings

#SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/home/'
SOCIAL_AUTH_LOGIN_URL = '/'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = json.loads(
    open(SECRETS, 'r').read())['GOOGLE_OAUTH2_KEY']
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = json.loads(
    open(SECRETS, 'r').read())['GOOGLE_OAUTH2_SECRET']

SOCIAL_AUTH_TWITTER_KEY = json.loads(
    open(SECRETS, 'r').read())['TWITTER_KEY']
SOCIAL_AUTH_TWITTER_SECRET = json.loads(
    open(SECRETS, 'r').read())['TWITTER_SECRET']

SOCIAL_AUTH_UID_LENGTH = 255

#LOGIN_ERROR_URL = '/login-error/'
# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'EST'

USE_I18N = True

USE_L10N = True

USE_TZ = True


BOWER_COMPONENTS_ROOT = BASE_DIR +"/components/"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
]




STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR + STATIC_URL

STATICFILES_DIRS = [
    BASE_DIR + "/assets",
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR + MEDIA_URL

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
            'verbose': {
                'format' : "[%(asctime)s] %(levelname)s[%(name)s:%(lineno)s] %(message)s",
                'datefmt' : "%d/%b/%Y %H:%M:%S"
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
    'handlers': {

        # Debug handlers
        'django_debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.debug.log',
            'formatter': 'verbose'
        },
        'builder_debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/builder.debug.log',
            'formatter': 'verbose'
        },
        'social_info': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/social.debug.log',
            'formatter': 'simple'
        },

        # Info handlers
        'django_info': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.info.log',
            'formatter': 'simple'
        },
        'builder_info': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/builder.info.log',
            'formatter': 'simple'
        },
        'social_info': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/social.info.log',
            'formatter': 'simple'
        },

    },
    'loggers': {

        # Debug loggers
        'django': {
            'handlers':['django_debug'],
            'propagate': True,
            'level':'DEBUG',
        },
        'builder': {
            'handlers': ['builder_debug'],
            'level': 'DEBUG',
        },
        'social': {
            'handlers': ['social_info'],
            'level': 'DEBUG',
        },

        # Debug loggers
        'django': {
            'handlers':['django_info'],
            'propagate': True,
            'level':'INFO',
        },
        'builder': {
            'handlers': ['builder_info'],
            'level': 'INFO',
        },
        'social': {
            'handlers': ['social_info'],
            'level': 'INFO',
        },

    }
}

# cripsy forms template pack
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# django-ckeditor settings
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_BROWSE_SHOW_DIRS= True
CKEDITOR_CONFIGS = {
    'default': {
        "removePlugins": "stylesheetparser",
        'skin': 'moono',
        # 'skin': 'office2013',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_YouCustomToolbarConfig': [
            {'name': 'document', 'items': ['Source', '-', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
            {'name': 'forms',
             'items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton',
                       'HiddenField']},
            '/',
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',
                       'Language']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert',
             'items': ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe']},
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
            {'name': 'about', 'items': ['About']},
        ],
        'toolbar': 'YouCustomToolbarConfig',  # put selected toolbar config here
        # 'toolbarGroups': [{ 'name': 'document', 'groups': [ 'mode', 'document', 'doctools' ] }],
        # 'height': 291,
        # 'width': '100%',
        # 'filebrowserWindowHeight': 725,
        # 'filebrowserWindowWidth': 940,
        # 'toolbarCanCollapse': True,
        # 'mathJaxLib': '//cdn.mathjax.org/mathjax/2.2-latest/MathJax.js?config=TeX-AMS_HTML',
        'tabSpaces': 4,
        'extraPlugins': ','.join(
            [
                # you extra plugins here
                'div',
                'autolink',
                'autoembed',
                'embedsemantic',
                'autogrow',
                # 'devtools',
                'widget',
                'lineutils',
                'clipboard',
                'dialog',
                'dialogui',
                'elementspath'
            ]),
    },
    'coding': {
        'skin': 'moono',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_YouCustomToolbarConfig': [
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert',
             'items': ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe']},
        ],
        'tabSpaces': 4,
        'extraPlugins': ','.join(
            [
                # you extra plugins here
                'bbcode'
            ]),
    }
}


# Builder specific
EMPTY_FIELDSET = "no_fieldset"
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
