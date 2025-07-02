from django import forms

from django.contrib.auth import password_validation
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=10)
    password = forms.CharField(widget = forms.PasswordInput, max_length=30)
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        user = User(username)
    
        if username and password:
            if not password_validation.validate_password(password=password, user=user):
                self.add_error("password", "This password is similar to username.")


class MessageForm(forms.Form):
    message = forms.CharField(widget = forms.Textarea, max_length=200)