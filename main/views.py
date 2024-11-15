from django.shortcuts import render
from django.views.generic import TemplateView, ListView

from administrator.models import *

# Create your views here.

class HomeView(TemplateView):
    template_name = 'main/home.html'

class AboutView(ListView):
    model = Team
    template_name = 'main/about.html'
    context_object_name = 'teams'
    
class ContactView(TemplateView):
    template_name = 'main/contact.html'

class TermView(TemplateView):
    template_name = 'main/term.html'
    
class PrivacyView(TemplateView):
    template_name = 'main/privacy.html'
