from django import forms

from .models import *

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['category', 'title', 'content', 'image', 'status']
        widgets = {
            'category': forms.CheckboxSelectMultiple(),
            }
    