from django import template

register = template.Library()

@register.filter
def endswith(value, arg):
    if not isinstance(value, str):
        return False
    return value.lower().endswith(arg.lower())

