from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """
    Replace occurrences of arg with space in value
    Usage: {{ value|replace:"_" }}
    """
    if arg in value:
        return value.replace(arg, " ")
    return value

@register.filter
def format_key(value):
    """
    Format dictionary keys for display
    Usage: {{ key|format_key }}
    """
    return value.replace("_", " ").title()