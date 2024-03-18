from datetime import datetime
import pytz
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth import login
from .forms import UserLoginForm, UserPasswordResetForm, UserLoginEmailForm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, DeleteView
from core.mixin import HttpsOptionMixin as CustomView
from .forms import UserRegistrationForm, VerifyCodeForm, ProfileChangeOrCreationForm, CustomUserChangeForm, \
    ChangePasswordForm
import random
from account.utils import send_otp_code
from .models import OptCode, User, Profile
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView


class SuccessLoginView(CustomView, LoginView):
    """
    Handles user login.
    Inherits from CustomView and LoginView classes.
    """
    http_method_names = ['get', 'post']
    next_page = reverse_lazy('home')

    def setup(self, request, *args, **kwargs):
        """Initialize the next page2, get profile."""
        self.next_page2 = reverse_lazy('create_profile')  # noqa
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
            return redirect(self.next_page2)
        return response

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch method to handle user authentication status.
        If the user is authenticated, redirect to the home page.
        Otherwise, proceed with the default dispatch behavior.
        """
        if request.user.is_authenticated:

            return redirect('home')

        else:
            return super().dispatch(request, *args, **kwargs)


class UserLoginView(CustomView):
    """
    View for user login.
    Renders login form and handles form submission for user login.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """Initialize the form, next page1, page2, template name."""
        self.form = UserLoginForm  # noqa
        self.next_page1 = reverse_lazy('login_verify_code')  # noqa
        self.next_page2 = reverse_lazy('login')  # noqa
        self.template_name = 'accounts/login.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        """
         Handle GET requests to display the login form.
         Renders the login form with an instance of the UserLoginForm.
         """
        return render(request, self.template_name, {'form': self.form()})

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
                return redirect(self.next_page1)
            else:
                messages.error(request, 'Phone number or password is not valid', extra_tags='error')
                return redirect(self.next_page2)
        return render(request, self.template_name, {'form': form})


class LoginVerifyCodeView(CustomView):
    """
    View for verifying login code.

    Renders the code verification form and handles form submission.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """Initialize the form, next page1, page2, page3, template name."""
        self.form = VerifyCodeForm  # noqa
        self.next_page1 = reverse_lazy('login_verify_code')  # noqa
        self.next_page2 = reverse_lazy('success_login')  # noqa
        self.next_page3 = reverse_lazy('login')  # noqa
        self.template_name = 'accounts/verifycode.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        """
        Handle GET requests to display the code verification form.

        Renders the code verification form.
        """
        return render(request, self.template_name, {'form': self.form()})

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
            cd = form.cleaned_data
            death_time = code_instance.created + timezone.timedelta(minutes=2)
            if cd['code'] == code_instance.code and death_time > datetime.now(tz=pytz.timezone('Asia/Tehran')):
                if code_instance:
                    user = User.objects.get(phone_number=code_instance.phone_number)
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    code_instance.delete()
                    messages.success(request, 'Code verified successfully', extra_tags='success')
                    return redirect(self.next_page2)
            elif death_time < datetime.now(tz=pytz.timezone('Asia/Tehran')):
                messages.error(request, 'Code is expired', extra_tags='error')
                return redirect(self.next_page3)
        else:
            messages.error(request, 'Code is not valid', extra_tags='error')
            return redirect(self.next_page1)


class UserLoginEmailView(CustomView):
    template_name = 'accounts/email/login_email.html'
    http_method_names = ['get', 'post']
    next_page = reverse_lazy('login_verify_code_email')
    form_class = UserLoginEmailForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            request.session['user_login_info'] = {
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password'],
            }
            random_code = random.randint(1000, 9999)
            OptCode.objects.create(email=form.cleaned_data['email'], code=random_code)
            messages.success(request, 'Code sent to your Email', extra_tags='success')
            return redirect(self.next_page)
        return render(request, self.template_name, {'form': form})


class UserPasswordResetEmailView(PasswordResetView):
    template_name = 'accounts/email/login_email.html'
    success_url = reverse_lazy('resat_done')
    form_class = UserPasswordResetForm
    http_method_names = ['get', 'post']
    email_template_name = 'accounts/email/otp_code_email.html'


class LoginVerifyCodeEmailView(CustomView):
    form_class = VerifyCodeForm
    template_name = 'accounts/verifycode.html'
    http_method_names = ['get', 'post']

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        user_session = request.session['user_login_info']
        code_instance = OptCode.objects.get(email=user_session['phone_number'])
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            death_time = code_instance.created + timezone.timedelta(minutes=2)
            if cd['code'] == code_instance.code and death_time > datetime.now(tz=pytz.timezone('Asia/Tehran')):
                if code_instance:
                    user = User.objects.get(email=code_instance.email)
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    code_instance.delete()
                    messages.success(request, 'Code verified successfully', extra_tags='success')
                    return redirect('success_login')
                return redirect('home')
            elif death_time < datetime.now(tz=pytz.timezone('Asia/Tehran')):
                messages.error(request, 'Code is expired', extra_tags='error')
                return redirect('login_verify_code')
        else:
            messages.error(request, 'Code is not valid', extra_tags='error')
            return redirect('login_verify_code')


class UserLogoutView(CustomView):
    """
    Handles user logout.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """Initialize the success_url."""
        self.success_url = reverse_lazy('home')  # noqa
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch method to handle user authentication status.
        Redirects non-authenticated users to the home page with an error message.
        """
        if not request.user.is_authenticated:
            messages.error(
                request,
                'You are not logged in.',
                extra_tags='error',
            )
            return redirect(self.success_url)
        else:
            return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for logging out.
        Logs out the user, clears session, and redirects to the home page with a success message.
        """
        if request.user.is_authenticated:
            logout(self.request)
            messages.success(request, 'Logout successfully', extra_tags='success')
            request.session.flush()
            return redirect(self.success_url)


class UserRegisterView(CustomView):
    """
    Handles user registration.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """Initialize the form, next page1, page2, template name."""
        self.form_class = UserRegistrationForm  # noqa
        self.next_page1 = reverse_lazy('verify_code')  # noqa
        self.next_page2 = reverse_lazy('register_user')  # noqa
        self.template_name = 'accounts/create_user.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        """
       Handle GET requests to display the user registration form.
       Renders the user registration form.
       """
        return render(request, self.template_name, {'form': self.form_class()})

    def post(self, request):
        """
        Handle POST requests to process the user registration form submission.
        If form is valid, generate and send OTP code, and store registration info in session.
        If form is not valid, display error messages.
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            random_code = random.randint(1000, 9999)
            send_otp_code(form.cleaned_data['phone_number'], random_code)

            OptCode.objects.create(phone_number=form.cleaned_data['phone_number'], code=random_code)
            request.session['user_registration_info'] = {
                'phone_number': form.cleaned_data['phone_number'],
                'email': form.cleaned_data['email'],
                'username': form.cleaned_data['username'],
                'password': form.cleaned_data['password2'],
            }
            messages.success(request, 'Code sent to your phone number', extra_tags='success')
            return redirect(self.next_page1)
        elif not form.is_valid():
            messages.error(request, 'Please Invalid form!!!', extra_tags='error')
            return redirect(self.next_page2)
        return render(request, self.template_name, {'form': form})


class UserRegistrationVerifyCodeView(CustomView):
    """
    Handles verification of registration code for user registration.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """Initialize the form, next page1, page2, context, template name."""
        self.form_class = VerifyCodeForm  # noqa
        self.next_page1 = reverse_lazy('home')  # noqa
        self.next_page2 = reverse_lazy('login_verify_code')  # noqa
        self.template_name = 'accounts/verifycode.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        """
        Handle GET requests to display the code verification form for user registration.
        Renders the code verification form.
        """
        return render(request, self.template_name, {'form': self.form_class()})

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
                User.objects.create_user(
                    phone_number=user_session['phone_number'],
                    email=user_session['email'],
                    username=user_session['username'],
                    password=user_session['password'],
                )

                code_instance.delete()
                messages.success(request, 'User created successfully', extra_tags='success')
                return redirect(self.next_page1)
            elif death_time < datetime.now(tz=pytz.timezone('Asia/Tehran')):
                messages.error(request, 'Code is expired', extra_tags='error')
                return redirect(self.next_page2)
        else:
            messages.error(request, 'Code is not valid', extra_tags='error')
            return redirect(self.next_page2)


class UserChangeView(CustomView):
    """
    View for changing user information.
    """
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """
        Initialize the form, next page1, page2, context, template name.
        Set up method to retrieve the current user instance.
        """
        self.form_class = CustomUserChangeForm  # noqa
        self.next_page1 = reverse_lazy('home')  # noqa
        self.next_page2 = reverse_lazy('change_user')  # noqa
        self.template_name = 'accounts/change_user.html'  # noqa
        self.user_instance = request.user  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to display the user change form.
        Renders the user change form with the current user's information.
        """
        form = self.form_class(instance=self.user_instance)
        return render(request, self.template_name, {'form': form})

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
            return redirect(self.next_page1)
        elif not form.is_valid():
            messages.error(request, 'Please Invalid form!!!', extra_tags='error')
            return redirect(self.next_page2)
        return render(request, self.template_name, {'form': form})


class ChangePasswordView(CustomView):
    """A view to manage password change for users."""
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """
        Initialize the form, next page1, page2, template name.
        """
        self.form_class = ChangePasswordForm  # noqa
        self.next_page1 = reverse_lazy('home')  # noqa
        self.next_page2 = reverse_lazy('change_pass')  # noqa
        self.template_name = 'accounts/change_password.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        """Render the change password form."""
        form = self.form_class(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Handle password change form submission."""
        form = self.form_class(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect(self.next_page1)
        elif not form.is_valid():
            messages.error(request, 'Please Invalid form!!!', extra_tags='error')
            return redirect(self.next_page2)
        return render(request, self.template_name, {'form': form})


class UserPasswordResetView(PasswordResetView):
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


class UserPasswordResetDoneView(PasswordResetDoneView):
    """
    View for displaying password reset done confirmation.
    Inherits from Django's built-in PasswordResetDoneView.
    Attributes:
        template_name (str): The name of the template to be rendered.
        http_method_names (list): List of HTTP methods allowed for this view.
    """
    template_name = 'accounts/email/password_resat_done.html'
    http_method_names = ['get']


class UserPasswordResetConfirmView(PasswordResetConfirmView):
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


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    """
    View for displaying password reset completion.
    Inherits from Django's built-in PasswordResetCompleteView.
    Attributes:
        template_name (str): The name of the template to be rendered.
        http_method_names (list): List of HTTP methods allowed for this view.
    """
    template_name = 'accounts/email/password_reset_complete.html'
    http_method_names = ['get']


class CreateProfileView(CustomView):
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
        self.template_name = 'accounts/create_profile.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        """
        Handles the creation of user profiles.
        """
        if request.user:
            try:
                profile = request.user.profile  # noqa
                return redirect(self.next_page1)
            except Profile.DoesNotExist:
                pass
        return super().dispatch(request, *args, **kwargs)  # noqa

    def get(self, request):
        """
        Renders the form for creating a user profile.
        """
        form = self.form_class(instance=request.user)
        return render(request, self.template_name, {'form': form})

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


class EditeProfileView(CustomView):
    """
    Handles user profile creation.
    """

    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        """
        Initialize the form, next page1, page2, template name.
        """
        self.form_class = ProfileChangeOrCreationForm  # noqa
        self.next_page1 = reverse_lazy('home')  # noqa
        self.next_page2 = reverse_lazy('create_profile')  # noqa
        self.template_name = 'accounts/edite_profile.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        """
        Renders the form for creating a user profile.
        """
        form = self.form_class(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        Processes the form submission for creating a user profile.
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


class ProfileDetailView(DetailView):
    """
    Displays user profile details.
    """

    http_method_names = ['get']

    def setup(self, request, *args, **kwargs):
        """
        Initialize the model, context object_name, template name.
        """
        self.model = Profile  # noqa
        self.context_object_name = 'profile'  # noqa
        self.template_name = 'accounts/profile_detail.html'  # noqa
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        """
        Retrieves the profile object for the currently logged-in user.
        """
        profile_get_object = Profile.objects.get(user=self.request.user)
        return get_object_or_404(User, pk=self.kwargs['pk']) and profile_get_object


class DeleteProfileView(DeleteView):
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


class DeleteUserView(DeleteView):
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
