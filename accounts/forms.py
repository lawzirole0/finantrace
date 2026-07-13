from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, CURRENCY_CHOICES

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    profession = forms.ChoiceField(choices=UserProfile.PROFESSION_CHOICES)
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES, initial='NGN')

    class Meta:
        model = User
        fields = ('email', 'profession', 'currency', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
            profile = UserProfile.objects.get(user=user)
            profile.profession = self.cleaned_data['profession']
            profile.currency = self.cleaned_data['currency']
            profile.save()
        return user
