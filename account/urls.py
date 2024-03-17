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
    LoginVerifyCodeView,
    SuccessLoginView,
    UserPasswordResetView,
    UserPasswordResetDoneView,
    UserPasswordResetConfirmView,
    UserPasswordResetCompleteView,
)

urlpatterns = [
    # Authentication URLs
    path("login/", UserLoginView.as_view(), name="login"),
    path("successlogin/", SuccessLoginView.as_view(), name="success_login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),

    # Registration URLs
    path('register/', UserRegisterView.as_view(), name='register_user'),
    path('verify/', UserRegistrationVerifyCodeView.as_view(), name='verify_code'),
    path('login_verify/', LoginVerifyCodeView.as_view(), name='login_verify_code'),

    # Account Management URLs
    path('changeuser/', UserChangeView.as_view(), name='change_user'),
    path("changepass/", ChangePasswordView.as_view(), name="change_pass"),
    path('users/<int:pk>/delete/', DeleteUserView.as_view(), name='delete_user'),

    # Profile Management URLs
    path("profiles/<int:pk>/", ProfileDetailView.as_view(), name="profile_detail"),
    path('profile/<int:pk>/delete/', DeleteProfileView.as_view(), name='delete_profile'),
    path("createprofile/", CreateProfileView.as_view(), name="create_profile"),

    # Password Reset URLs
    path("resatpassword/", UserPasswordResetView.as_view(), name="resat_password"),
    path("resatpassword/done/", UserPasswordResetDoneView.as_view(), name="resat_done"),
    path("confirm/<uidb64>/<token>/", UserPasswordResetConfirmView.as_view(), name="resat_password_confirm"),
    path("confirm/resatcomplete/", UserPasswordResetCompleteView.as_view(), name="resat_complete"),

]
