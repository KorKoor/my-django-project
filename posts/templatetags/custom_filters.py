# En custom_filters.py
from django import template

register = template.Library()

@register.filter
def message_type(message, user):
    if hasattr(message, 'sender'):
        return "sent" if message.sender == user else "received"
    return "unknown"
