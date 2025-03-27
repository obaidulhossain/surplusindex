from django import template
import locale

register = template.Library()

@register.filter
def currency(value):
    if value is None:  # Check if the value is None
        return "$0.00"  # Return a default formatted value
    
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')  # Set the locale for formatting
        return locale.currency(value, grouping=True)
    except (ValueError, TypeError):  # Catch other potential errors
        return f"${value:,.2f}"  # Fallback formatting