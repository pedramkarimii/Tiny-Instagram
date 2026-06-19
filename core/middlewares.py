from django.shortcuts import redirect
from django.contrib import messages

LOGIN_EXEMPT_URLS = [
    '/login/',
    '/register',
    '/logout/',
    '/',
]


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and request.path_info not in LOGIN_EXEMPT_URLS:
            messages.warning(request, 'You should login first', extra_tags='warning')
            return redirect('login')
        response = self.get_response(request)
        return response
