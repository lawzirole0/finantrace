from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DailyReport
from .services.trace_engine import TraceResult

@login_required
def new_report_view(request):
    profile = request.user.profile
    context = {
        "trial_uses_remaining": profile.trial_uses_remaining,
    }
    return render(request, 'reconciliation/new_report.html', context)

@login_required
def trace_result_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        try:
            opening = float(request.POST.get('opening', 0))
            deposits = float(request.POST.get('deposits', 0))
            withdrawals = float(request.POST.get('withdrawals', 0))
            closing = float(request.POST.get('closing', 0))
        except (ValueError, TypeError):
            messages.error(request, 'Please enter valid numeric values.')
            return redirect('new_report')

        result = TraceResult(opening, deposits, withdrawals, closing)

        if profile.trial_uses_remaining > 0 or profile.subscription_status != 'free':
            report = DailyReport.objects.create(
                user=request.user,
                opening_balance=opening,
                total_deposits=deposits,
                total_withdrawals=withdrawals,
                closing_balance=closing,
            )
            if profile.subscription_status == 'free':
                profile.trial_uses_remaining -= 1
                profile.save(update_fields=['trial_uses_remaining'])

            context = result.to_context()
            context['report'] = report
            context['recent_reports'] = list(DailyReport.objects.filter(
                user=request.user
            ).only('created_at', 'closing_balance', 'is_balanced').order_by('-created_at')[:5])
            return render(request, 'reconciliation/result.html', context)
        else:
            messages.error(request, 'No free uses remaining. Please upgrade to continue.')
            return redirect('payments_pricing')

    return redirect('new_report')
