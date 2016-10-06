from django.contrib.auth.models import models
from django.contrib.auth.models import User
from django import forms
from django.db.models.signals import post_save


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        app_label = 'app'

    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

    post_save.connect(create_user_profile, sender=User)

class UserProfileForm(forms.ModelForm):

    class Meta:
        app_label = 'app'
        model = UserProfile
        exclude = []
        widgets = {'user': forms.HiddenInput}

class UserForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        app_label = 'app'
        model = User
        fields = ['username', 'email', 'password']



