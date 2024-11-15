from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, FormView
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import Group
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetConfirmView, LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from .token import account_activation_token

from .forms import RegisterForm
from .models import User
from administrator.models import Log

# Create your views here.

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'account/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        if user.profile_picture:
            user.profile_picture = self.request.FILES.get('profile_picture')
        if not 'agree' in self.request.POST:
            messages.error(self.request, 'You Must Agree To Our Terms And Conditions Before You Register')
            return redirect('register')
        user.save()
        if user.role == 'Writer':
            writer_group, created = Group.objects.get_or_create(name='Writer')
            user.groups.add(writer_group)
        else:
            reader_group, created = Group.objects.get_or_create(name='Reader')
            user.groups.add(reader_group)
        user.save()
        log = Log(user=user, action=f"'{user.username}' created an account as a '{user.role}'")
        log.save()
        self.send_verification_email(user)
        messages.success(self.request, 'Registration Successful! Please Check Your Email To Verify Your Account.')
        return super().form_valid(form)

    def send_verification_email(self, user):
        current_site = get_current_site(self.request)
        subject = "ByteWrite: Verify Your Account"
        message = render_to_string('account/mail/account_verify_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
        log = Log(user=user, action=f"ByteWrite sent a verification email to '{user.username}'")
        log.save()

class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(get_user_model(), pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            user = None 
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            log = Log(user=user, action=f"'{user.username}' verified his/her account")
            log.save()
            messages.success(request, 'Your Account Has Been Verified. You Can Log In Now.')
            return redirect('login')
        else:
            messages.error(request, 'Activation Link Is Invalid!.')
            return redirect('login')

class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.POST.get('remember'):
            self.request.session.set_expiry(1209600)
        else:
            self.request.session.set_expiry(0)
        log = Log(user=self.request.user, action=f"'{self.request.user.username}' logged in")
        log.save()
        return response
    
    def get_success_url(self):
        user = self.request.user
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        else:
            if user.groups.filter(name='Writer').exists():
                return reverse_lazy('writer_home')
            elif user.groups.filter(name='Reader').exists():
                return reverse_lazy('reader_home')
            elif user.groups.filter(name='Admin').exists():
                return reverse_lazy('admin_home')
        return super().get_success_url()
    
def LogOutView(request):
    log = Log(user=request.user, action=f"'{request.user.username}' logged out")
    log.save()
    logout(request)
    return redirect('home')

class ForgotPasswordView(FormView):
    form_class = PasswordResetForm
    template_name = 'account/forgot_password.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        email = self.request.POST.get('email')
        try:
            user = get_object_or_404(User, email=email)
            log = Log(user=user, action=f"'{user.username}' filled a forgot password form")
            log.save()
            self.send_verification_email(user)
            messages.success(self.request, 'Check Your Email Inbox Or Spam For Instructions On How To Reset Your Password')
            return super().form_valid(form)
        except:
            messages.error(self.request, 'Email Not Found')
            return redirect('forgot_password')
    
    def send_verification_email(self, user):
        current_site = get_current_site(self.request)
        subject = "ByteWrite: Forgot Password Request"
        message = render_to_string('account/mail/forgot_password_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
            'date': timezone.now().date(),
        })
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
        log = Log(user=user, action=f"ByteWrite sent a password recovery mail to '{user.username}'")
        log.save()

class ForgotPasswordConfirmView(PasswordResetConfirmView):
    template_name = 'account/forgot_password_confirm.html'

    def form_valid(self, form):
        uid = self.kwargs.get('uidb64')
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        form.save()
        log = Log(user=user, action=f'{user.username} reset their password')
        log.save()
        messages.success(self.request, 'Your Password Has Been Reset Successfully. You Can Log In Now.')
        return redirect(reverse_lazy('login'))
