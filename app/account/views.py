from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
import pytz
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth import login
from .forms import UserLoginForm, UserPasswordResetForm, UserLoginEmailForm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, DeleteView
from app.core.mixin import HttpsOptionLoginMixin as MustBeLogoutCustomView, \
    HttpsOptionNotLogoutMixin as MustBeLogingCustomView
from .forms import UserRegistrationForm, VerifyCodeForm, ProfileChangeOrCreationForm, CustomUserChangeForm, \
    ChangePasswordForm
import random
from app.account.utils import send_otp_code
from .models import OptCode, User, Profile, Relation
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView

"""
 Explanation of the imports:
 - `datetime`: Module for working with dates and times
 - `send_mail`: Function for sending emails
 - `settings`: Django settings module for accessing project settings
 - `pytz`: Module for timezone support
 - `messages`: Module for displaying messages to users
 - `logout`, `update_session_auth_hash`, `login`: Functions for user authentication management
 - `UserLoginForm`, `UserPasswordResetForm`, `UserLoginEmailForm`: Custom forms for user login and password reset
 - `render`, `redirect`, `get_object_or_404`: Functions for rendering templates, redirecting requests, and 
        fetching objects from the database
 - `reverse_lazy`: Function for generating URLs
 - `timezone`: Module for working with time zones
 - `DetailView`, `DeleteView`: Generic class-based views for displaying detail pages and deleting objects
 - `HttpsOptionLoginMixin`, `HttpsOptionNotLogoutMixin`: Custom mixins for managing HTTPS options 
        based on login/logout status
 - `UserRegistrationForm`, `VerifyCodeForm`, `ProfileChangeOrCreationForm`, `CustomUserChangeForm`, 
        `ChangePasswordForm`: Custom forms for user registration, verification code, profile management, 
        user information change, and password change
 - `random`: Module for generating random numbers
 - `send_otp_code`: Function for sending OTP (One-Time Password) codes
 - `OptCode`, `User`, `Profile`: Model classes representing OTP codes, users, and user profiles
 - `LoginView`, `PasswordResetView`, `PasswordResetDoneView`, `PasswordResetConfirmView`, 
        `PasswordResetCompleteView`: Django's built-in views for user authentication and password reset
"""


class SuccessLoginView(MustBeLogoutCustomView, LoginView):
    """
    Handles user login.
    Inherits from CustomView and LoginView classes.
    """
    http_method_names = ['get', 'post']
    next_page = reverse_lazy('home')

    def setup(self, request, *args, **kwargs):
        """Initialize the next_page_create_profile, get profile."""
        self.next_page_create_profile = reverse_lazy('create_profile')  # noqa
        self.get_profile = hasattr(request.user, 'profile')  # noqa
        return super().setup(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Process the form submission after successful validation.
        If the user has a profile with age and name, display a success message.
        If the profile is incomplete, redirect to complete it.
        """
        response = super().form_valid(form)
        if self.get_profile and self.request.user.profile.age and self.request.user.profile.name:
            messages.success(self.request, 'You have logged in successfully.', extra_tags='success')
        else:
            messages.warning(self.request,
                             'Please complete your profile.',
                             extra_tags='warning')
            return redirect(self.next_page_create_profile)
        return response


class UserLoginView(MustBeLogoutCustomView):
    """
    View for user login.
    Renders login form and handles form submission for user login.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """Initialize the form, next_page_login_verify_code, next_page_login, next_page_home,
         template_name, template name."""
        self.form = UserLoginForm  # noqa
        self.next_page_login_verify_code = reverse_lazy('login_verify_code')  # noqa
        self.next_page_login = reverse_lazy('login')  # noqa
        self.template_login = 'accounts/login.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        """
         Handle GET requests to display the login form.
         Renders the login form with an instance of the UserLoginForm.
         """
        return render(request, self.template_login, {'form': self.form()})

    def post(self, request):
        """
        Handle POST requests to process the login form submission.
        If form is valid, store user login information in session and send an OTP code.
        If the user exists, generate and send OTP code, then redirect to verify code page.
        If form is not valid, display error messages and redirect back to login page.
        """
        form = self.form(request.POST)
        if form.is_valid():
            request.session['user_login_info'] = {
                'phone_number': form.cleaned_data['phone_number'],
                'password': form.cleaned_data['password'],
            }
            phone_number = form.cleaned_data['phone_number']
            user = User.objects.filter(phone_number=phone_number).exists()
            if user:
                random_code = random.randint(1000, 9999)
                send_otp_code(phone_number, random_code)
                OptCode.objects.create(phone_number=phone_number, code=random_code)
                messages.success(request, 'Code sent to your phone number', extra_tags='success')
                return redirect(self.next_page_login_verify_code)
            else:
                messages.error(request, 'Phone number or password is not valid', extra_tags='error')
                return redirect(self.next_page_login)
        return render(request, self.template_login, {'form': form})


class UserLogoutView(MustBeLogingCustomView):
    """
    Handles user logout.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """Initialize the success_url."""
        self.next_page_home = reverse_lazy('home')  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for logging out.
        Logs out the user, clears session, and redirects to the home page with a success message.
        """
        if request.user.is_authenticated:
            logout(self.request)
            messages.success(request, 'Logout successfully', extra_tags='success')
            request.session.flush()
            return redirect(self.next_page_home)


class LoginVerifyCodeView(MustBeLogoutCustomView):
    """
    View for verifying login code.

    Renders the code verification form and handles form submission.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """Initialize the form, next_page_login_verify_code, next_page_success_login,
        next_page_login, next_page_home, template name."""
        self.form = VerifyCodeForm  # noqa
        self.next_page_login_verify_code = reverse_lazy('login_verify_code')  # noqa
        self.next_page_success_login = reverse_lazy('success_login')  # noqa
        self.next_page_login = reverse_lazy('login')  # noqa
        self.next_page_home = reverse_lazy('home')  # noqa
        self.template_verifycode = 'accounts/verifycode.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        """
        Handle GET requests to display the code verification form.

        Renders the code verification form.
        """
        return render(request, self.template_verifycode, {'form': self.form()})

    def post(self, request):
        """
        Handle POST requests to process the code verification form submission.

        Retrieves user login information from session and verifies the entered code.
        If the code is valid and not expired, logs the user in and redirects to success page.
        If the code is expired or invalid, displays error messages and redirects back to verification page.
        """
        user_session = request.session['user_login_info']
        code_instance = OptCode.objects.get(phone_number=user_session['phone_number'])
        form = self.form(request.POST)
        if form.is_valid():  # noqa
            cd = form.cleaned_data  # noqa
            death_time = code_instance.created + timezone.timedelta(minutes=2)
            if cd['code'] == code_instance.code and death_time > datetime.now(tz=pytz.timezone('Asia/Tehran')):
                if code_instance and code_instance.is_used == False:  # noqa
                    user = User.objects.get(phone_number=code_instance.phone_number)
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    code_instance.delete()
                    code_instance.is_used = True
                    messages.success(request, 'Code verified successfully', extra_tags='success')
                    return redirect(self.next_page_success_login)
            elif death_time < datetime.now(tz=pytz.timezone('Asia/Tehran')):
                messages.error(request, 'Code is expired', extra_tags='error')
                return redirect(self.next_page_login)
        else:
            messages.error(request, 'Code is not valid', extra_tags='error')
            return redirect(self.next_page_login_verify_code)


class UserRegisterView(MustBeLogoutCustomView):
    """
    Handles user registration.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """Initialize the form_class, next_page_verify_code, next_page_register_user,
        next_page_home, template name."""
        self.form_class = UserRegistrationForm  # noqa
        self.next_page_verify_code = reverse_lazy('verify_code')  # noqa
        self.next_page_register_user = reverse_lazy('register_user')  # noqa
        self.next_page_home = reverse_lazy('home')  # noqa
        self.template_create_user = 'accounts/create_user.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        """
       Handle GET requests to display the user registration form.
       Renders the user registration form.
       """
        return render(request, self.template_create_user, {'form': self.form_class()})

    def post(self, request):
        """
        Handle POST requests to process the user registration form submission.
        If form is valid, generate and send OTP code, and store registration info in session.
        If form is not valid, display error messages.
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            random_code = random.randint(1000, 9999)
            OptCode.objects.create(phone_number=form.cleaned_data['phone_number'], code=random_code)
            send_otp_code(form.cleaned_data['phone_number'], random_code)
            request.session['user_registration_info'] = {
                'phone_number': form.cleaned_data['phone_number'],
                'email': form.cleaned_data['email'],
                'username': form.cleaned_data['username'],
                'password': form.cleaned_data['password2'],
            }
            messages.success(request, 'Code sent to your phone number', extra_tags='success')
            return redirect(self.next_page_verify_code)

        return render(request, self.template_create_user, {'form': form})


class UserRegistrationVerifyCodeView(MustBeLogoutCustomView):
    """
    Handles verification of registration code for user registration.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """Initialize the form_class, next_page_home, next_page_login_verify_code, template name."""
        self.form_class = VerifyCodeForm  # noqa
        self.next_page_home = reverse_lazy('home')  # noqa
        self.next_page_login_verify_code = reverse_lazy('login_verify_code')  # noqa
        self.template_verifycode = 'accounts/verifycode.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        """
        Handle GET requests to display the code verification form for user registration.
        Renders the code verification form.
        """
        return render(request, self.template_verifycode, {'form': self.form_class()})

    def post(self, request):
        """
        Handle POST requests to process the code verification form submission for user registration.
        Retrieves user registration information from session and verifies the entered code.
        If the code is valid and not expired, creates the user and redirects to home page.
        If the code is expired or invalid, displays error messages and redirects back to verification page.
        """
        user_session = request.session['user_registration_info']
        code_instance = OptCode.objects.get(phone_number=user_session['phone_number'])
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            death_time = code_instance.created + timezone.timedelta(minutes=2)

            if cd['code'] == code_instance.code and death_time > datetime.now(tz=pytz.timezone('Asia/Tehran')):
                if code_instance.is_used == False:  # noqa
                    User.objects.create_user(
                        phone_number=user_session['phone_number'],
                        email=user_session['email'],
                        username=user_session['username'],
                        password=user_session['password'],
                    )

                code_instance.delete()
                code_instance.is_used = True
                messages.success(request, 'User created successfully', extra_tags='success')
                return redirect(self.next_page_home)
            elif death_time < datetime.now(tz=pytz.timezone('Asia/Tehran')):
                messages.error(request, 'Code is expired', extra_tags='error')
                code_instance.delete()
                return redirect(self.next_page_login_verify_code)
        else:
            messages.error(request, 'Code is not valid', extra_tags='error')
            return redirect(self.next_page_login_verify_code)


class ChangePasswordView(MustBeLogingCustomView):
    """A view to manage password change for users."""
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """
        Initialize the form_class, next page1, page2, template name.
        """
        self.form_class = ChangePasswordForm  # noqa
        self.next_page_home = reverse_lazy('home')  # noqa
        self.next_page_change_pass = reverse_lazy('change_pass')  # noqa
        self.template_change_password = 'accounts/change_password.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        """Render the change password form."""
        form = self.form_class(request.user)
        return render(request, self.template_change_password, {'form': form})

    def post(self, request):
        """Handle password change form submission."""
        form = self.form_class(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect(self.next_page_home)
        return render(request, self.template_change_password, {'form': form})


class UserLoginEmailView(MustBeLogoutCustomView):
    """
    Defines a view for user login via email.
    Handles GET and POST requests.
    Sets up necessary attributes such as form_class, URLs, and templates.
    Includes a method to send OTP email and create OptCode instance.
    Handles form submission and OTP email sending logic.
    Displays appropriate messages based on email verification status.
    """

    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """
        Initialize the form_class, next_page_login_verify_code_email, template_login_email.
        """
        self.form_class = UserLoginEmailForm  # noqa
        self.next_page_login_verify_code_email = reverse_lazy('login_verify_code_email')  # noqa
        self.next_page_login_email = reverse_lazy('login_email')  # noqa
        self.template_login_email = 'accounts/email/login_email.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def send_otp_email(self, email, otp):

        user = User.objects.get(email=email)
        if user:
            subject = 'Your OTP for Verification'
            message = f'Your OTP for login is (Expiry date two minutes): {otp}'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)
            OptCode.objects.create(email=email, code=otp)
            messages.success(self.request, 'Code sent to your Email', extra_tags='success')
        elif not user:
            messages.success(self.request, 'Invalid email or password', extra_tags='success')
            return redirect(self.next_page_login_email)
        else:
            messages.success(self.request, 'Invalid email or password', extra_tags='success')
            return redirect(self.next_page_login_email)

    def get(self, request):
        return render(request, self.template_login_email, {'form': self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            random_code = random.randint(1000, 9999)
            self.send_otp_email(email, random_code)
            request.session['user_login_info'] = {
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password'],
            }
            return redirect(self.next_page_login_verify_code_email)

        return render(request, self.template_login_email, {'form': form})


class LoginVerifyCodeEmailView(MustBeLogoutCustomView):
    """
    Defines a view for verifying login codes sent via email.
    Handles GET and POST requests.
    Sets up necessary attributes such as form_class, URLs, and templates.
    Handles form submission and code verification logic.
    Displays appropriate messages based on verification status.
    """

    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """
        Initialize the form_class, next_page_login_verify_code_email, template_login_email.
        """
        self.form_class = VerifyCodeForm  # noqa
        self.next_page_login_email = reverse_lazy('login_email')  # noqa
        self.next_page_success_login = reverse_lazy('success_login')  # noqa
        self.next_page_login_verify_code = reverse_lazy('login_verify_code_email')  # noqa
        self.template_verifycode = 'accounts/verifycode.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_verifycode, {'form': self.form_class()})

    def post(self, request):
        user_session = request.session.get('user_login_info')
        try:
            code_instance = OptCode.objects.get(email=user_session['email'])
        except OptCode.DoesNotExist:
            messages.error(request, 'Code is not valid', extra_tags='error')
            return redirect(self.next_page_login_email)
        form = self.form_class(request.POST)
        if form.is_valid():  # noqa
            cd = form.cleaned_data  # noqa
            death_time = code_instance.created + timezone.timedelta(minutes=2)
            if cd['code'] == code_instance.code and death_time > datetime.now(tz=pytz.timezone('Asia/Tehran')):
                if code_instance and code_instance.is_used == False:  # noqa
                    user = User.objects.get(email=code_instance.email)
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    code_instance.is_used = True
                    code_instance.delete()
                    messages.success(request, 'Code verified successfully', extra_tags='success')
                    return redirect(self.next_page_success_login)
                else:
                    messages.error(request, 'Code is already used', extra_tags='error')
                    return redirect(self.next_page_login_email)
            elif death_time < datetime.now(tz=pytz.timezone('Asia/Tehran')):
                messages.error(request, 'Code is expired', extra_tags='error')
                code_instance.delete()
                return redirect(self.next_page_login_email)
        else:
            messages.error(request, 'Code is not aAA valid', extra_tags='error')
            return redirect(self.next_page_login_verify_code)
        # else:
        #     messages.error(request, 'Code is not valid', extra_tags='error')
        #     return redirect(self.next_page_login_verify_code)


class UserPasswordResetView(PasswordResetView, MustBeLogoutCustomView):
    """
   View for handling user password reset.
   Inherits from Django's built-in PasswordResetView.
   Attributes:
       template_name (str): The name of the template to be rendered.
       success_url (str): The URL to redirect to upon successful password reset.
       form_class (class): The form class to be used for password reset.
       http_method_names (list): List of HTTP methods allowed for this view.
       email_template_name (str): The name of the email template to be used for password reset email.
   """
    template_name = 'accounts/email/password_reset.html'
    success_url = reverse_lazy('resat_done')
    form_class = UserPasswordResetForm
    http_method_names = ['get', 'post']
    email_template_name = 'accounts/email/password_reset_email.html'


class UserPasswordResetDoneView(PasswordResetDoneView, MustBeLogoutCustomView):
    """
    View for displaying password reset done confirmation.
    Inherits from Django's built-in PasswordResetDoneView.
    Attributes:
        template_name (str): The name of the template to be rendered.
        http_method_names (list): List of HTTP methods allowed for this view.
    """
    template_name = 'accounts/email/password_resat_done.html'
    http_method_names = ['get']


class UserPasswordResetConfirmView(PasswordResetConfirmView, MustBeLogoutCustomView):
    """
    View for handling user password reset confirmation.
    Inherits from Django's built-in PasswordResetConfirmView.
    Attributes:
        template_name (str): The name of the template to be rendered.
        success_url (str): The URL to redirect to upon successful password reset.
        http_method_names (list): List of HTTP methods allowed for this view.
    """
    template_name = 'accounts/email/password_reset_confirm.html'
    success_url = reverse_lazy('resat_complete')
    http_method_names = ['get', 'post']


class UserPasswordResetCompleteView(PasswordResetCompleteView, MustBeLogoutCustomView):
    """
    View for displaying password reset completion.
    Inherits from Django's built-in PasswordResetCompleteView.
    Attributes:
        template_name (str): The name of the template to be rendered.
        http_method_names (list): List of HTTP methods allowed for this view.
    """
    template_name = 'accounts/email/password_reset_complete.html'
    http_method_names = ['get']


class UserChangeView(MustBeLogingCustomView):
    """
    View for changing user information.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """
        Initialize the form_class, next_page_home, next_page_change_user, user_instance, template name.
        Set up method to retrieve the current user instance.
        """
        self.form_class = CustomUserChangeForm  # noqa
        self.next_page_home = reverse_lazy('home')  # noqa
        self.next_page_change_user = reverse_lazy('change_user')  # noqa
        self.template_change_user = 'accounts/change_user.html'  # noqa
        self.user_instance = request.user  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to display the user change form.
        Renders the user change form with the current user's information.
        """
        form = self.form_class(instance=self.user_instance)
        return render(request, self.template_change_user, {'form': form})

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to process form submission for changing user information.
        If form is valid, save changes and display success message.
        If form is not valid, render form again with error messages.
        """
        form = self.form_class(request.POST, instance=self.user_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'User information updated successfully', extra_tags='success')
            return redirect(self.next_page_home)
        return render(request, self.template_change_user, {'form': form})


class CreateProfileView(MustBeLogingCustomView):
    """
    Handles the creation of user profiles.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """
        Initialize the form, next page1, page2, template name.
        """
        self.form_class = ProfileChangeOrCreationForm  # noqa
        self.next_page1 = reverse_lazy('home')  # noqa
        self.next_page2 = reverse_lazy('create_profile')  # noqa
        self.template_create_profile = 'accounts/create_profile.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        """
        Renders the form for creating a user profile.
        """
        form = self.form_class(instance=request.user)
        return render(request, self.template_create_profile, {'form': form})

    def post(self, request):
        """
        Handles form submission for creating a user profile.
        """
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None

        form = self.form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile_picture = request.FILES.get('profile_picture')
            if profile_picture:
                profile.profile_picture = profile_picture
            profile.save()
            messages.success(
                request,
                'Your profile has been created successfully',
                extra_tags='success')
            return redirect(self.next_page1)
        else:
            messages.error(
                request,
                'Your profile has not been created successfully',
                extra_tags='error')
            return redirect(self.next_page2)


class ProfileDetailView(DetailView, MustBeLogingCustomView):
    """
    setup method:
    Sets up the view by defining the model, context object name, and template name.

    get_object method:
    Retrieves the profile object based on the user ID passed in the URL kwargs.

    get_context_data method:
    Adds additional context data to be passed to the template, including counts of followers and following users,
     as well as lists of followers' and following users' usernames.
    """

    http_method_names = ['get']

    def setup(self, request, *args, **kwargs):
        self.model = Profile  # noqa
        self.context_object_name = 'profile'  # noqa
        self.template_name = 'accounts/profile_detail.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        user_id = self.kwargs.get('pk')
        return get_object_or_404(Profile, user_id=user_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()

        followers_count = Relation.objects.filter(following=profile.user).count()
        following_count = Relation.objects.filter(followers=profile.user).count()
        context['followers_count'] = followers_count
        context['following_count'] = following_count

        followers_usernames = Relation.objects.filter(following=profile.user).values_list('followers__id',
                                                                                          'followers__username')
        following_usernames = Relation.objects.filter(followers=profile.user).values_list('following__id',
                                                                                          'following__username')

        context['followers_usernames'] = followers_usernames
        context['following_usernames'] = following_usernames

        return context


class DeleteProfileView(DeleteView, MustBeLogingCustomView):
    """
    View for deleting a user's profile.
    """

    http_method_names = ['get', 'post']
    success_url = reverse_lazy('home')

    def setup(self, request, *args, **kwargs):
        """
        Initialize the model, template name.
        """
        self.model = Profile  # noqa
        self.template_name = 'accounts/delete_account.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Handle the deletion of the profile.
        """
        self.object = self.get_object()  # noqa
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, 'Your profile has been successfully deleted.')
        return redirect(success_url)


class DeleteUserView(DeleteView, MustBeLogingCustomView):
    """
    View for soft deleting a user.
    """
    http_method_names = ['get', 'post']
    success_url = reverse_lazy('home')

    def setup(self, request, *args, **kwargs):
        """
        Initialize the model, template name.
        """
        self.model = User  # noqa
        self.template_name = 'accounts/delete_user.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Handle soft deletion of the user.
        """
        self.object = self.get_object()  # noqa
        success_url = self.get_success_url()
        self.object.soft_delete.filter(pk=self.object.pk).delete()
        messages.success(request, 'User has been successfully deleted.')
        return redirect(success_url)
