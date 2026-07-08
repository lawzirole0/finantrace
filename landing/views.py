from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def landing_view(request):
    return render(request, 'landing/index.html')

def pricing_view(request):
    return render(request, 'payments/pricing.html')

def growth_guide_view(request):
    return render(request, 'landing/growth_guide.html')
