from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """
    Splits a string based on the argument provided.
    Usage: {{ value|split:"delimiter" }}
    """
    return value.split(arg)