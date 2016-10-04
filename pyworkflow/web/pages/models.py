from django.contrib.auth.models import models
from django.contrib.auth.models import User
from django import forms


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        app_label = 'app'


class UserProfileForm(forms.ModelForm):

    class Meta:
        app_label = 'app'
        model = UserProfile
        exclude = []


class UserForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        app_label = 'app'
        model = User
        fields = ['username', 'email', 'password']



