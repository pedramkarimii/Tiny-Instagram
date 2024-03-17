from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import reverse


LOGIN_EXEMPT_URLS = [
    '/login/',
    '/register/',
    '/verify/',
    '/login_verify_code/',
    '/login_verify/',
    '/success_login/',
    '/resatpassword/',
    '/resatpassword/done/',
    '/admin/login/',
    '/confirm/MQ/',
    '/confirm/resatcomplete/',
    '/',
]
PROFILE_EXEMPT_URLS = [
    '/createpost/',
    'show_post/<int:pk>/',
    'explorer/<int:pk>/',
    'follow/<int:user_id>/',
    'unfollow/<str:user_id>/',
    'like/<str:post_id>/',
    'dislike/<str:post_id>/',
    'post/<int:pk>/update/',
    'post/<int:pk>/delete/',
]
AFTER_LOGIN_REDIRECT_URL = [
    '/login/',
    '/register/',
    '/verify/',
    '/login_verify_code/',
    '/login_verify/',
    '/success_login/',
    '/resatpassword/',
    '/resatpassword/done/',
    '/admin/login/',
    '/confirm/MQ/',
    '/confirm/resatcomplete/',

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
        if request.user.is_authenticated and request.path_info not in PROFILE_EXEMPT_URLS:
            try:
                profile = request.user.profile # noqa
            except ObjectDoesNotExist:
                if request.path_info != reverse('create_profile'):
                    messages.warning(request, 'You should create your profile first', extra_tags='warning')
                    return HttpResponseRedirect(reverse('create_profile'))

        response = self.get_response(request)

        if response.status_code in [400, 404, 405, 406, 500, 401, 403]:
            messages.warning(request, 'An error occurred. Please try again.', extra_tags='error')
            return HttpResponseRedirect(reverse('home'))
        return response
