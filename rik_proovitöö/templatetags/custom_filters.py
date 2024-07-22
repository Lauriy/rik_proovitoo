from django import template

register = template.Library()


@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return ''


@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except ValueError:
        return ''
