from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PlatformConnection

PLATFORM_INFO = {
    'stripe': {'icon': 'credit_card', 'color': '#635bff', 'bg': '#f0eeff'},
    'paypal': {'icon': 'payments', 'color': '#003087', 'bg': '#e6edf6'},
    'shopify': {'icon': 'store', 'color': '#5e8e3e', 'bg': '#edf5e9'},
    'instagram': {'icon': 'photo_camera', 'color': '#e4405f', 'bg': '#fde8ed'},
    'tiktok': {'icon': 'music_note', 'color': '#010101', 'bg': '#e6e6e6'},
    'linkedin': {'icon': 'work', 'color': '#0a66c2', 'bg': '#e6f0fa'},
    'etsy': {'icon': 'handcraft', 'color': '#d5641c', 'bg': '#fcedf0'},
    'square': {'icon': 'apps', 'color': '#007bff', 'bg': '#e6f2ff'},
}

@login_required
def connections_view(request):
    connections = PlatformConnection.objects.filter(user=request.user)
    return render(request, 'connections/index.html', {
        'connections': connections,
        'platform_info': PLATFORM_INFO,
    })

@login_required
def connect_platform_view(request):
    if request.method == 'POST':
        platform = request.POST.get('platform')
        label = request.POST.get('label', '')
        account_name = request.POST.get('account_name', '')
        account_email = request.POST.get('account_email', '')

        if not platform or platform not in dict(PlatformConnection.PLATFORM_CHOICES):
            messages.error(request, 'Please select a valid platform.')
            return redirect('connect_platform')

        if PlatformConnection.objects.filter(user=request.user, platform=platform, account_id=account_email or account_name).exists():
            messages.warning(request, f'This {dict(PlatformConnection.PLATFORM_CHOICES).get(platform, platform)} account is already connected.')
            return redirect('connections')

        PlatformConnection.objects.create(
            user=request.user,
            platform=platform,
            label=label or f"My {dict(PlatformConnection.PLATFORM_CHOICES).get(platform, platform)}",
            account_name=account_name,
            account_email=account_email,
            access_token='placeholder_token',
            is_active=True,
        )
        messages.success(request, f'{dict(PlatformConnection.PLATFORM_CHOICES).get(platform, platform)} connected successfully!')
        return redirect('connections')

    return render(request, 'connections/connect.html', {
        'platforms': PlatformConnection.PLATFORM_CHOICES,
        'platform_info': PLATFORM_INFO,
    })

@login_required
def disconnect_platform_view(request, connection_id):
    connection = get_object_or_404(PlatformConnection, id=connection_id, user=request.user)
    platform_name = connection.get_platform_display()
    connection.delete()
    messages.success(request, f'{platform_name} disconnected successfully.')
    return redirect('connections')

@login_required
def sync_connection_view(request, connection_id):
    connection = get_object_or_404(PlatformConnection, id=connection_id, user=request.user)
    from django.utils import timezone
    connection.last_synced_at = timezone.now()
    connection.save(update_fields=['last_synced_at'])
    messages.success(request, f'{connection.get_platform_display()} synced successfully.')
    return redirect('connections')
