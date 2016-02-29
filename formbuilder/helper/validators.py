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

