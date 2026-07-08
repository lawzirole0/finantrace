import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Subscription
from .services import paystack as pstk


@login_required
def subscribe_view(request):
    if request.method != 'POST':
        return redirect('payments_pricing')

    plan = request.POST.get('plan')
    if plan not in ('startup', 'growing'):
        messages.error(request, 'Invalid plan selected.')
        return redirect('payments_pricing')

    sub, _ = Subscription.objects.get_or_create(user=request.user)
    sub.plan = plan
    sub.save(update_fields=['plan'])

    amount = pstk.PLAN_AMOUNTS[plan]
    plan_code = pstk.PLAN_CODES.get(plan, '')
    email = request.user.email

    result = pstk.initialize_transaction(email, amount, plan_code=plan_code, metadata={
        "user_id": request.user.id,
        "username": request.user.username,
        "plan": plan,
    })

    if result.get('status'):
        auth_url = result['data']['authorization_url']
        sub.paystack_email = email
        sub.save(update_fields=['paystack_email'])
        return redirect(auth_url)

    messages.error(request, f'Payment initialization failed: {result.get("message", "Unknown error")}')
    return redirect('payments_pricing')


@login_required
def callback_view(request):
    reference = request.GET.get('reference')
    if not reference:
        messages.error(request, 'No payment reference found.')
        return redirect('dashboard')

    result = pstk.verify_transaction(reference)

    if not result.get('status'):
        messages.error(request, f'Payment verification failed: {result.get("message", "Unknown error")}')
        return redirect('dashboard')

    data = result['data']
    if data['status'] != 'success':
        messages.error(request, 'Payment was not successful.')
        return redirect('payments_pricing')

    metadata = data.get('metadata') or {}
    plan = metadata.get('plan') or 'startup'
    customer_code = data['customer']['customer_code']
    auth_code = data['authorization']['authorization_code']
    email = data['customer']['email']

    sub, _ = Subscription.objects.get_or_create(user=request.user)
    sub.plan = plan
    sub.paystack_customer_code = customer_code
    sub.paystack_authorization_code = auth_code
    sub.paystack_email = email
    sub.is_active = True
    sub.save()

    if plan_code := pstk.PLAN_CODES.get(plan):
        sub_result = pstk.create_subscription(customer_code, plan_code)
        if sub_result.get('status'):
            sub.paystack_subscription_code = sub_result['data']['subscription_code']

            from django.utils import timezone
            from datetime import timedelta
            sub.renews_at = timezone.now() + timedelta(days=30)
            sub.save(update_fields=['paystack_subscription_code', 'renews_at'])

    profile = request.user.profile
    profile.subscription_status = plan
    profile.save(update_fields=['subscription_status'])

    messages.success(request, f'You are now on the {plan.title()} plan! Welcome aboard.')
    return redirect('dashboard')


@csrf_exempt
def webhook_view(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    # Verify Paystack signature
    signature = request.headers.get('x-paystack-signature', '')
    body = request.body

    import hashlib
    import hmac
    expected = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        body,
        hashlib.sha512,
    ).hexdigest()

    if signature != expected:
        return HttpResponse(status=401)

    event = json.loads(body)

    if event['event'] == 'subscription.create':
        data = event['data']
        customer_code = data['customer']['customer_code']
        sub_code = data['subscription_code']
        plan = 'startup' if 'startup' in data['plan']['name'].lower() else 'growing'

        for sub in Subscription.objects.filter(paystack_customer_code=customer_code):
            sub.paystack_subscription_code = sub_code
            sub.is_active = True
            from django.utils import timezone
            from datetime import timedelta
            sub.renews_at = timezone.now() + timedelta(days=30)
            sub.save(update_fields=['paystack_subscription_code', 'is_active', 'renews_at'])

    elif event['event'] == 'subscription.disable':
        data = event['data']
        sub_code = data['subscription_code']
        Subscription.objects.filter(paystack_subscription_code=sub_code).update(is_active=False)

    elif event['event'] == 'charge.success':
        data = event['data']
        if data.get('authorization', {}).get('reusable'):
            email = data['customer']['email']
            auth_code = data['authorization']['authorization_code']
            customer_code = data['customer']['customer_code']
            sub = Subscription.objects.filter(paystack_customer_code=customer_code).first()
            if sub:
                sub.paystack_authorization_code = auth_code
                sub.save(update_fields=['paystack_authorization_code'])

    return HttpResponse(status=200)
