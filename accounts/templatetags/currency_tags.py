from django import template
from ..models import CURRENCY_SYMBOLS

register = template.Library()

@register.filter
def currency(value, currency_code='USD'):
    symbol = CURRENCY_SYMBOLS.get(currency_code, '$')
    try:
        val = float(value)
        if val == int(val):
            return f"{symbol}{int(val):,}"
        return f"{symbol}{val:,.2f}"
    except (ValueError, TypeError):
        return f"{symbol}0"

@register.filter
def curr_symbol(currency_code):
    return CURRENCY_SYMBOLS.get(currency_code, '$')
