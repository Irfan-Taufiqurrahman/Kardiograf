from django import forms
from .models import kardiografUser

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = kardiografUser
        fields = ['address', 'birthdate', 'numberPhone', 'imageUser']