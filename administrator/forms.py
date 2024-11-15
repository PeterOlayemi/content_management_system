from django import forms

from .models import *

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class ContactForm(forms.ModelForm):
    twitter_link = forms.CharField(required= False, help_text='Optional. Start With "http://" or "https://"')
    facebook_link = forms.CharField(required= False, help_text='Optional. Start With "http://" or "https://"')
    instagram_link = forms.CharField(required= False, help_text='Optional. Start With "http://" or "https://"')
    linkedin_link = forms.CharField(required= False, help_text='Optional. Start With "http://" or "https://"')

    class Meta:
        model = Contact
        fields = ['address', 'phone', 'email', 'twitter_link', 'facebook_link', 'instagram_link', 'linkedin_link']

class TeamForm(forms.ModelForm):
    twitter_link = forms.CharField(required= False, help_text='Optional. Start With "http://" or "https://"')
    facebook_link = forms.CharField(required= False, help_text='Optional. Start With "http://" or "https://"')
    instagram_link = forms.CharField(required= False, help_text='Optional. Start With "http://" or "https://"')
    linkedin_link = forms.CharField(required= False, help_text='Optional. Start With "http://" or "https://"')

    class Meta:
        model = Team
        fields = ['image', 'full_name', 'role', 'bio', 'twitter_link', 'facebook_link', 'instagram_link', 'linkedin_link']
