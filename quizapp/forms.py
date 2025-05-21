from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254, required=True)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No User Registered with this email.")
        return email

class ResetPasswordForms(forms.Form):
    new_password = forms.CharField(label='New Password', max_length=25)
    confirm_password = forms.CharField(label='Confirm Password', max_length=25)

    def clean(self):
        cleaned_data = super().clean()  # Correct usage of super
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and confirm_password != new_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data  # Ensure you return cleaned_data at the end
