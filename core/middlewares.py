from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

LOGIN_EXEMPT_URLS = [
    '/login/',
    '/register/',
    '/verify/',
    '/admin/login/?next=/admin/',
    '/login_verify_code/',
    '/login_verify/',
    '/success_login/',
]
AFTER_LOGIN_REDIRECT_URL = [
    '/login/',
    '/register/',
    '/verify/',
    '/admin/login/?next=/admin/',
    '/login_verify_code/',
    '/login_verify/',
    '/success_login/',
]


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and request.path_info not in LOGIN_EXEMPT_URLS:
            messages.warning(request, 'You should login first', extra_tags='warning')
            return HttpResponseRedirect(reverse('login'))
        elif request.user.is_authenticated and request.path_info in AFTER_LOGIN_REDIRECT_URL:
            messages.warning(request, 'You should logout first', extra_tags='warning')
            return HttpResponseRedirect(reverse('home'))
        response = self.get_response(request)
        if response.status_code in [400, 404, 405, 406, 500, 401, 403]:
            messages.error(request, 'An error occurred. Please try again.', extra_tags='error')
            return HttpResponseRedirect(reverse('home'))
        return response
