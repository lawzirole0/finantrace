from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Idea
from .services.ai_generator import get_personalized_ideas

@login_required
def idea_feed_view(request):
    ideas = Idea.objects.filter(is_active=True)
    ai_ideas = None

    if request.method == 'POST' and 'get_ai_suggestions' in request.POST:
        profile = request.user.profile
        interests = request.POST.get('interests', '')
        interests_list = [i.strip() for i in interests.split(',') if i.strip()] if interests else None
        ai_ideas = get_personalized_ideas(profile.profession, interests_list)
        if ai_ideas:
            messages.success(request, 'AI generated 3 personalized ideas based on your profile!')

    context = {
        "ideas": ideas,
        "ai_ideas": ai_ideas,
    }
    return render(request, 'ideas/feed.html', context)

@login_required
def idea_detail_view(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id, is_active=True)
    steps = [s.strip() for s in idea.steps_to_start.split('\n') if s.strip()]
    metrics = [m.strip() for m in idea.key_metrics.split('\n') if m.strip()]

    profile = request.user.profile
    match_score = 0
    if profile.profession == 'freelancer' and idea.startup_cost_min <= 10000:
        match_score = 85
    elif profile.profession in ('retail', 'food') and 'local' in idea.title.lower():
        match_score = 78
    elif profile.profession in ('service', 'creator') and idea.ease_of_entry == 'easy':
        match_score = 82
    else:
        match_score = 65

    similar = Idea.objects.filter(
        industry=idea.industry, is_active=True
    ).exclude(id=idea.id)[:3]

    circle_offset = 352 - (352 * match_score / 100)

    context = {
        "idea": idea,
        "steps": steps,
        "metrics": metrics,
        "match_score": match_score,
        "circle_offset": circle_offset,
        "similar": similar,
    }
    return render(request, 'ideas/detail.html', context)
