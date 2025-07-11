from django import forms

from django.contrib.auth import password_validation
from django.contrib.auth.models import User


class RegisterForm(forms.Form):
    ## Flaw 2
    username = forms.CharField(max_length=10)
    email = forms.EmailField(widget=forms.EmailInput)
    password = forms.CharField(widget=forms.PasswordInput, max_length=30)
    secret_question = forms.CharField(max_length=100)
    secret_answer = forms.CharField(widget=forms.TextInput, max_length=30)
    
    ## Fix Flaw 2
    """
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
    
        if username and email and password:
            user = User(password=password, username=username, email=email)
            password_validation.validate_password(password=password, user=user)
    """
    ## End Fix Flaw 2


class MessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, max_length=200)


## Fix Flaw 4
## The following three classes to be completely commented-out for the fix:
## PasswordRecoveryForm, SecretQuestionForm, PasswordChangeForm

class PasswordRecoveryForm(forms.Form):
    username = forms.CharField(max_length=10)
    email = forms.EmailField(widget=forms.EmailInput)


class SecretQuestionForm(forms.Form):
    secret_answer = forms.CharField(widget=forms.TextInput, max_length=30)


class PasswordChangeForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, max_length=30)

## End Fix Flaw 4