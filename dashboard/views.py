from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from reconciliation.models import DailyReport
from finance.models import Transaction
from paths.models import Profession, StepItem, UserProgress
from paths.profession_data import PROFESSION_DATA

@login_required
def dashboard_view(request):
    profile = request.user.profile
    reports_qs = DailyReport.objects.filter(user=request.user)
    balanced_count = reports_qs.filter(is_balanced=True).count()
    total_reports = reports_qs.count()
    recent_reports = reports_qs.order_by('-created_at')[:5]
    recent_transactions = Transaction.objects.filter(
        user=request.user
    ).select_related('user').order_by('-date')[:5]

    profession_slug = profile.profession
    data = PROFESSION_DATA.get(profession_slug, PROFESSION_DATA["freelancer"])
    total_items = StepItem.objects.filter(step__profession__slug=profession_slug).count()
    completed_items = UserProgress.objects.filter(
        user=request.user, step_item__step__profession__slug=profession_slug, completed=True
    ).count()
    path_progress = int((completed_items / total_items) * 100) if total_items else 0

    context = {
        "reports": recent_reports,
        "transactions": recent_transactions,
        "balanced_count": balanced_count,
        "total_reports": total_reports,
        "profession_data": data,
        "path_progress": path_progress,
    }
    return render(request, 'dashboard/index.html', context)
