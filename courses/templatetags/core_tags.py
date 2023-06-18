from django import template
from django.conf import settings
from django.http import QueryDict

register = template.Library()


@register.filter
def verbose_name(instance, field_name):
    return instance._meta.get_field(field_name).verbose_name


@register.filter
def check_perms_list(perms, perms_list):
    for perm in perms_list:
        if perm in perms:
            return True
    return False


@register.filter
def page_url(request, page):
    query: QueryDict = request.GET.copy()
    query["page"] = page
    return query.urlencode()


@register.simple_tag
def get_setting_value(value):
    return getattr(settings, value, None)


@register.simple_tag(takes_context=True)
def set_query_param(context, param, value):
    request = context["request"]
    params = request.GET.copy()
    params[param] = value
    return params


@register.simple_tag()
def delete_query_param(q_dict, param):
    params = q_dict.copy()
    params.pop(param, None)
    return params
