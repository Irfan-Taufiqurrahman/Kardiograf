from django import forms
from authentication.models import roleUser

class LoginForm(forms.Form):
    username = forms.CharField(
        widget = forms.TextInput(
            attrs={
                "class" : "form-control"
            }
        )
    )
    password = forms.CharField(
        widget = forms.PasswordInput(
            attrs={
                "class" : "form-control"
            }
        )  
    )

class SignupForm(forms.Form):
    username = forms.CharField(
        widget = forms.TextInput(
            attrs={
                "class" : "form-control"
            }
        )
    )
    password = forms.CharField(
        widget = forms.PasswordInput(
            attrs={
                "class" : "form-control"
            }
        )  
    )
    email = forms.CharField(
        widget = forms.TextInput(
            attrs={
                "class" : "form-control"
            }
        )
    )
    address = forms.CharField(
        widget = forms.TextInput(
            attrs={
                "class" : "form-control"
            }
        )
    )
    birthdate = forms.CharField(
        widget = forms.TextInput(
            attrs={
                "class" : "form-control"
            }
        )
    )

    class Meta:
        model = roleUser
        fields = ('username', 'email', 'password', 'is_admin', 'is_doctor', 'is_patient')