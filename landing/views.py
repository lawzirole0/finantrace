from django.shortcuts import render
from django.http import HttpResponse

def health_check(request):
    return HttpResponse('ok')

def landing_view(request):
    return render(request, 'landing/index.html')

def pricing_view(request):
    return render(request, 'payments/pricing.html')

def growth_guide_view(request):
    return render(request, 'landing/growth_guide.html')
