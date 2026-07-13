from .models import CURRENCY_SYMBOLS

def profile_context(request):
    """Makes user profile fields available directly in templates."""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            currency_code = profile.currency or 'NGN'
            return {
                'user_profession': profile.profession,
                'trial_uses_remaining': profile.trial_uses_remaining,
                'trial_uses_percent': profile.trial_uses_percent,
                'currency_code': currency_code,
                'currency_symbol': CURRENCY_SYMBOLS.get(currency_code, '₦'),
            }
        except Exception:
            pass
    return {
        'currency_code': 'NGN',
        'currency_symbol': '₦',
    }
