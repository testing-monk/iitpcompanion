from django import template

register = template.Library()

@register.filter
def split(value, delimiter=","):
    return value.split(delimiter)

@register.filter
def trim(value):
    return value.strip()
