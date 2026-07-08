from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import CURRENCY_CHOICES

@login_required
def settings_view(request):
    if request.method == 'POST':
        currency = request.POST.get('currency')
        if currency and any(c[0] == currency for c in CURRENCY_CHOICES):
            profile = request.user.profile
            profile.currency = currency
            profile.save(update_fields=['currency'])
            messages.success(request, f'Currency updated to {dict(CURRENCY_CHOICES).get(currency, currency)}')
        return redirect('settings')
    return render(request, 'settings/index.html', {
        'currency_choices': CURRENCY_CHOICES,
    })
