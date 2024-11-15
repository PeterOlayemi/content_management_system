from django.urls import path

from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/(<uidb64>[0-9A-Za-z_\-]+)/(<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/', ActivateAccountView.as_view(), name='activate'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogOutView, name='logout'),
    path('password/reset/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('password/reset/confirm/<uidb64>/<token>/', ForgotPasswordConfirmView.as_view(), name='forgot_password_confirm'),
]
