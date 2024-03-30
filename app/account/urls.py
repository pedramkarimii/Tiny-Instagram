from django.urls import path
from app.account.views import UserLoginView, UserLogoutView, UserRegisterView, UserRegistrationVerifyCodeView, \
    UserChangeView, ChangePasswordView, CreateProfileView, ProfileDetailView, DeleteProfileView, LoginVerifyCodeView, \
    DeleteUserView, SuccessLoginView, UserPasswordResetView, UserPasswordResetDoneView, UserPasswordResetConfirmView, \
    UserPasswordResetCompleteView, UserLoginEmailView, LoginVerifyCodeEmailView

urlpatterns = [
    # Authentication URLs
    # These URLs handle user authentication, such as logging in, logging out, and verifying successful login.
    path("login/", UserLoginView.as_view(), name="login"),
    path("loginemail/", UserLoginEmailView.as_view(), name="login_email"),
    path("successlogin/", SuccessLoginView.as_view(), name="success_login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),

    # Registration URLs
    # These URLs handle user registration and verification of registration codes.
    path('register/', UserRegisterView.as_view(), name='register_user'),
    path('verify/', UserRegistrationVerifyCodeView.as_view(), name='verify_code'),
    path('login_verify/', LoginVerifyCodeView.as_view(), name='login_verify_code'),
    path('login_verify_email/', LoginVerifyCodeEmailView.as_view(), name='login_verify_code_email'),

    # Account Management URLs
    # These URLs handle user account management,such as changing user information,changing passwords,and deleting users.
    path('changeuser/', UserChangeView.as_view(), name='change_user'),
    path("changepass/", ChangePasswordView.as_view(), name="change_pass"),
    path('users/<int:pk>/delete/', DeleteUserView.as_view(), name='delete_user'),

    # Profile Management URLs
    # These URLs handle user profile management, such as creating profiles, viewing profiles, and deleting profiles.
    path("profiles/<int:pk>/", ProfileDetailView.as_view(), name="profile_detail"),
    path('profile/<int:pk>/delete/', DeleteProfileView.as_view(), name='delete_profile'),
    path("createprofile/", CreateProfileView.as_view(), name="create_profile"),

    # Password Reset URLs
    # These URLs handle password reset functionality, such as requesting password resets, confirming password resets,
    # and completing password resets.
    path("resatpassword/", UserPasswordResetView.as_view(), name="resat_password"),
    path("resatpassword/done/", UserPasswordResetDoneView.as_view(), name="resat_done"),
    path("confirm/<uidb64>/<token>/", UserPasswordResetConfirmView.as_view(), name="resat_password_confirm"),
    path("confirm/resatcomplete/", UserPasswordResetCompleteView.as_view(), name="resat_complete"),

]
