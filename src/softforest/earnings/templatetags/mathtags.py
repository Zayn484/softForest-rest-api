from django import template
from django.contrib.auth.models import Group


register = template.Library()


@register.filter(name='percentof')
def percentof(arg1, arg2):
    res = arg1 / arg2 * 100
    return round(res, 1)

