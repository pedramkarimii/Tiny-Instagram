from django.urls import path
from .views import (
    UserLoginView,
    UserLogoutView,
    UserRegisterView,
    UserRegistrationVerifyCodeView,
    UserChangeView,
    ChangePasswordView,
    CreateProfileView,
    ProfileDetailView,
    DeleteProfileView,
    DeleteUserView,
    LoginVerifyCodeView, SuccessLoginView,
)

""" 
URL pattern for user login
URL pattern for user logout
URL pattern for register a user 
URL pattern for verify a user
URL pattern for change a user
URL pattern for change pass user
"""
urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("successlogin/", SuccessLoginView.as_view(), name="success_login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path('register/', UserRegisterView.as_view(), name='register_user'),
    path('verify/', UserRegistrationVerifyCodeView.as_view(), name='verify_code'),
    path('login_verify/', LoginVerifyCodeView.as_view(), name='login_verify_code'),
    path('changeuser/', UserChangeView.as_view(), name='change_user'),
    path("changepass/", ChangePasswordView.as_view(), name="change_pass"),
    path("createprofile/", CreateProfileView.as_view(), name="create_profile"),
    path('profile/<int:pk>/delete/', DeleteProfileView.as_view(), name='delete_profile'),
    path('users/<int:pk>/delete/', DeleteUserView.as_view(), name='delete_user'),
    path("profiles/<int:pk>/", ProfileDetailView.as_view(), name="profile_detail"),
]
