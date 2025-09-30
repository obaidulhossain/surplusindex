from django import template
import locale
from datetime import timedelta
register = template.Library()

@register.filter
def add_hours(value, hours):
    """Add hours to a datetime"""
    if not value:
        return value
    return value + timedelta(hours=int(hours))


@register.filter
def currency(value):
    if value is None:  # Check if the value is None
        return "$0.00"  # Return a default formatted value
    
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')  # Set the locale for formatting
        return locale.currency(value, grouping=True)
    except (ValueError, TypeError):  # Catch other potential errors
        return f"${value:,.2f}"  # Fallback formatting
    
@register.filter
def digits(value, digits):
    """
    Converts a number to a string with a fixed number of digits by padding with zeros.

    :param value: The number to be formatted
    :param digits: The total number of digits (default is 5)
    :return: A string representation of the number with leading zeros
    """
    try:
        return str(value).zfill(digits)
    except (TypeError, ValueError):
        return value  # Return the original value if there's an error