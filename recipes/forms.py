from django import forms
from django.contrib.auth.models import User
from .models import UserPreferences, UserProfile  # Importing UserProfile from models.py

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError('Passwords do not match')
        return cleaned_data

class UserPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        fields = ['diet', 'favorite_cuisine', 'skill_level']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']  # Handling the profile picture upload

from django import forms

class MoodForm(forms.Form):
    MOOD_CHOICES = [
        ("happy", "Happy"),
        ("sad","Sad"),
        ("lazy", "Lazy"),
        ("stressed", "Stressed"),
        ("healthy", "Healthy"),
        ("angry", "Angry"),
    ]
    mood = forms.ChoiceField(choices=MOOD_CHOICES, label="Select your mood")

from django import forms
from .models import UserProfile

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']

from django import forms
from .models import UploadedContent

class UploadContentForm(forms.ModelForm):
    class Meta:
        model = UploadedContent
        fields = ['title', 'description', 'image', 'ingredients', 'steps']


from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']