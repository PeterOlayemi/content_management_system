from django.urls import path

from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('term/', TermView.as_view(), name='term'),
    path('privacy/', PrivacyView.as_view(), name='privacy'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
]
