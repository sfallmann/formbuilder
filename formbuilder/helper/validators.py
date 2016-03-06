import re
from django.core.exceptions import ValidationError



def is_alpha(value):
    if not value.isalpha():
        raise ValidationError(
            ('%(value)s must be one word consisting of alpha characters'),
            params={'value': value},
        )

def is_alpha_num(value):
    if not value.isalnum():
        raise ValidationError(
            ('%(value)s must be one word consisting of alphanumeric characters'),
            params={'value': value},
        )

def is_alpha_num_words(value):
    if re.match('^[\w \d]+$', value) is None:
        raise ValidationError(
            ('%(value)s must be words consisting of alphanumeric characters'),
            params={'value': value},
        )

def is_alpha_num_whitespace(value):
    if re.match('^[\w_-\d]+$', value) is None:
        raise ValidationError(
            ('%(value)s must be words consisting of alphanumeric characters, -, or _'),
            params={'value': value},
        )

def is_lower(value):

    if value != value.lower():
        raise ValidationError(
            ('%(value)s must be lowercase'),
            params={'value': value},
        )
