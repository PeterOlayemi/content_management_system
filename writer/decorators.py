from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from urllib.parse import urlencode
from django.contrib import messages

class WriterRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.groups.filter(name='Writer'):
            return super().dispatch(request, *args, **kwargs)
        else:
            login_url = '/login/'
            query_string = urlencode({'next': request.get_full_path()})
            redirect_url = f"{login_url}?{query_string}"
            messages.success(request, 'Writer Permission Required')
            return redirect(redirect_url)
