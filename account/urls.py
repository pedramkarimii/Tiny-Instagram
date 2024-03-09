from django.urls import path
from .views import (
    UserLoginView,
    UserLogoutView,
    UserRegisterView,
    UserRegistrationVerifyCodeView,
    UserChangeView, ChangePasswordView,

)


urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('verify/', UserRegistrationVerifyCodeView.as_view(), name='verify_code'),
    path('changeuser/', UserChangeView.as_view(), name='change_user'),
    path("changepass/", ChangePasswordView.as_view(), name="change_pass"),
]
