from django import forms

from django.contrib.auth import password_validation
from django.contrib.auth.models import User


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=10)
    password = forms.CharField(widget = forms.PasswordInput, max_length=30)
    
    #
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        user = User(password=password, username=username)
    
        if username and password:
            password_validation.validate_password(password=password, user=user)
    #


class MessageForm(forms.Form):
    message = forms.CharField(widget = forms.Textarea, max_length=200)