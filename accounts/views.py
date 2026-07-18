from django.shortcuts import redirect


def login_view(request):
    return redirect('account_login')


def signup_view(request):
    return redirect('account_signup')


def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('landing')
