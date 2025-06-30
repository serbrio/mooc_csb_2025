from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=10)
    password = forms.CharField(widget = forms.PasswordInput, max_length=30)


class MessageForm(forms.Form):
    message = forms.CharField(widget = forms.Textarea, max_length=200)