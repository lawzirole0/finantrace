from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Transaction
from .services.calculator import get_cash_flow_summary

@login_required
def finance_overview_view(request):
    transactions = Transaction.objects.filter(
        user=request.user
    ).select_related('user').order_by('-date')[:20]
    summary = get_cash_flow_summary(transactions)
    context = {
        "transactions": transactions,
        "summary": summary,
    }
    return render(request, 'finance/overview.html', context)
