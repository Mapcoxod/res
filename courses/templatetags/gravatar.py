import hashlib
from urllib.parse import urlencode

from django import template
from django.conf import settings

register = template.Library()

@register.filter
def gravatar(user):
    email = user.email.lower().encode('utf-8')
    default = 'retro'
    size = 100
    url = 'https://www.gravatar.com/avatar/{md5}?{params}'.format(
        md5=hashlib.md5(email).hexdigest(),
        params=urlencode({'d': default, 's': str(size)})
    )

    return url


@register.filter
def verbose_name(instance, field_name):
    print(instance)
    return instance._meta.get_field(field_name).verbose_name
