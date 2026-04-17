from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        "class": "w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none",
        "placeholder": "Enter your email"
    }))

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "class": "w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none",
            "placeholder": "Enter username"
        })

        self.fields["password1"].widget.attrs.update({
            "class": "w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none",
        })

        self.fields["password2"].widget.attrs.update({
            "class": "w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none",
        })



class LoginForm(AuthenticationForm):
    username = forms.EmailField(required=True,
        widget= forms.EmailInput(attrs={
           "class": "w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none",
           "placeholder": "Enter your email"
        })
    )

    password = forms.CharField(required=True,
        widget= forms.PasswordInput(attrs={
           "class": "w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none",
           "placeholder": "Enter your password"
        })
    )