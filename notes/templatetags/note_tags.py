from django import template

register = template.Library()


@register.filter
def truncate_chars(value, max_length):
    if len(str(value)) > max_length:
        return value[:max_length] + '...'
    return value
