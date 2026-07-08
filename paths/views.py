from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Profession, Step, StepItem, UserProgress
from .profession_data import PROFESSION_DATA

@login_required
def path_view(request):
    profile = request.user.profile
    profession_slug = profile.profession

    data = PROFESSION_DATA.get(profession_slug)
    if not data:
        data = PROFESSION_DATA["freelancer"]

    profession_obj, _ = Profession.objects.get_or_create(
        slug=profession_slug,
        defaults={"name": data["name"], "description": data["description"]},
    )

    steps = Step.objects.filter(profession=profession_obj).prefetch_related('items').order_by('order')
    if not steps.exists():
        for step_data in data["steps"]:
            step = Step.objects.create(
                profession=profession_obj,
                order=step_data["order"],
                title=step_data["title"],
                description=step_data.get("description", ""),
            )
            for i, item_text in enumerate(step_data["items"]):
                StepItem.objects.create(step=step, text=item_text, order=i)
        steps = Step.objects.filter(profession=profession_obj).prefetch_related('items').order_by('order')

    total_items = StepItem.objects.filter(step__profession=profession_obj).count()
    completed_items = UserProgress.objects.filter(
        user=request.user, step_item__step__profession=profession_obj, completed=True
    ).count()
    progress_pct = int((completed_items / total_items) * 100) if total_items else 0

    user_progress = {
        up.step_item_id: up.completed
        for up in UserProgress.objects.filter(
            user=request.user, step_item__step__profession=profession_obj
        ).only('step_item_id', 'completed')
    }

    context = {
        "profession": data,
        "steps": steps,
        "progress_pct": progress_pct,
        "user_progress": user_progress,
    }
    return render(request, 'paths/path_detail.html', context)
