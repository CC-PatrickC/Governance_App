from django import template
from django.db.models import Avg

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """Divide the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def average_score(queryset, field_name):
    """Calculate the average score for a given field from a queryset of ProjectScore objects"""
    try:
        if not queryset:
            return None
        # Convert the queryset to a list of values for the specified field
        values = [getattr(score, field_name) for score in queryset if getattr(score, field_name) is not None]
        if not values:
            return None
        return sum(values) / len(values)
    except (ValueError, TypeError, AttributeError):
        return None 