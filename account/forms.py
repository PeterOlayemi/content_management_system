from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import *

class RegisterForm(UserCreationForm):
    website_link = forms.CharField(required= False, help_text='Optional. Start With "http://" or "https://"')
    twitter_link = forms.CharField(required= False, help_text='Optional. Start With "http://" or "https://"')
    facebook_link = forms.CharField(required= False, help_text='Optional. Start With "http://" or "https://"')
    instagram_link = forms.CharField(required= False, help_text='Optional. Start With "http://" or "https://"')
    linkedin_link = forms.CharField(required= False, help_text='Optional. Start With "http://" or "https://"')
    usable_password = None

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role', 'full_name', 'bio', 'profile_picture', 'website_link', 'twitter_link', 'facebook_link', 'instagram_link', 'linkedin_link']

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        full_name = cleaned_data.get('full_name')
        bio = cleaned_data.get('bio')
        profile_picture = cleaned_data.get('profile_picture')

        # If role is writer, ensure bio and full_name are required
        if role == 'Writer':
            if not full_name:
                self.add_error('full_name', 'Full name is required for writers.')
            if not bio:
                self.add_error('bio', 'Bio is required for writers.')
            if not profile_picture:
                self.add_error('profile_picture', 'Profile Picture is required for writers.')
       
        return cleaned_data

class ReaderUpdateForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ['username', 'email']

class WriterUpdateForm(forms.ModelForm):
    full_name = forms.CharField(required=True)
    profile_picture = forms.ImageField(required=True)
    website_link = forms.CharField(required= False, help_text='Optional. Start With "http://" or "https://"')
    twitter_link = forms.CharField(required= False, help_text='Optional. Start With "http://" or "https://"')
    facebook_link = forms.CharField(required= False, help_text='Optional. Start With "http://" or "https://"')
    instagram_link = forms.CharField(required= False, help_text='Optional. Start With "http://" or "https://"')
    linkedin_link = forms.CharField(required= False, help_text='Optional. Start With "http://" or "https://"')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'bio', 'profile_picture', 'website_link', 'twitter_link', 'facebook_link', 'instagram_link', 'linkedin_link']
