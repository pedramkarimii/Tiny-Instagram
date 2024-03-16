from datetime import datetime
import pytz
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth import login
from .forms import UserLoginForm, UserPasswordResetForm
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
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


#
class SuccessLoginView(CustomView, LoginView):
    """
    Handles user login.
    """
    # template_name = 'accounts/login.html'
    http_method_names = ['get', 'post']
    next_page = reverse_lazy('home')

    def form_valid(self, form):
        """
        Add a success message after successful login.
        """
        response = super().form_valid(form)
        if hasattr(self.request.user, 'profile') and self.request.user.profile.age and self.request.user.profile.name:
            messages.success(self.request, 'You have logged in successfully.', extra_tags='success')
        else:
            messages.warning(self.request,
                             'Please complete your profile.',
                             extra_tags='warning')
            return redirect('create_profile')
        return response

    def dispatch(self, request, *args, **kwargs):
        """
        Redirects authenticated users to the home page with a success message.
        """
        if request.user.is_authenticated:

            return redirect('home')

        else:
            return super().dispatch(request, *args, **kwargs)


class UserLoginView(CustomView):
    template_name = 'accounts/login.html'
    http_method_names = ['get', 'post']
    next_page = reverse_lazy('login_verify_code')
    form_class = UserLoginForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            request.session['user_login_info'] = {
                'phone_number': form.cleaned_data['phone_number'],
                'password': form.cleaned_data['password'],
            }
            random_code = random.randint(1000, 9999)
            send_otp_code(form.cleaned_data['phone_number'], random_code)
            OptCode.objects.create(phone_number=form.cleaned_data['phone_number'], code=random_code)
            messages.success(request, 'Code sent to your phone number', extra_tags='success')
            return redirect(self.next_page)
        return render(request, self.template_name, {'form': form})


class LoginVerifyCodeView(CustomView):
    form_class = VerifyCodeForm
    template_name = 'accounts/verifycode.html'
    http_method_names = ['get', 'post']

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        user_session = request.session['user_login_info']
        code_instance = OptCode.objects.get(phone_number=user_session['phone_number'])
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            deatht_time = code_instance.created + timezone.timedelta(minutes=2)
            if cd['code'] == code_instance.code and deatht_time > datetime.now(tz=pytz.timezone('Asia/Tehran')):
                if code_instance:
                    user = User.objects.get(phone_number=code_instance.phone_number)
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    code_instance.delete()
                    messages.success(request, 'Code verified successfully', extra_tags='success')
                    return redirect('success_login')
                return redirect('home')

            else:
                messages.error(request, 'Code is not valid', extra_tags='error')
                return redirect('login_verify_code')


class UserLogoutView(CustomView):
    """
    Handles user logout.
    """
    http_method_names = ['get', 'post']
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        """
        Redirects non-authenticated users to the home page with a success message.
        """
        if not request.user.is_authenticated:
            messages.error(
                request,
                'You are not logged in.',
                extra_tags='error',
            )
            return redirect('home')
        else:
            return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Logs out the user and redirects to the home page with a success message.
        """
        if request.user.is_authenticated:
            logout(self.request)
            messages.success(request, 'Logout successfully', extra_tags='success')
            request.session.flush()
            return redirect('home')


class UserRegisterView(CustomView):
    form_class = UserRegistrationForm
    template_name = 'accounts/create_user.html'
    http_method_names = ['get', 'post']

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
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
            return redirect('verify_code')
        return render(request, self.template_name, {'form': form})


class UserRegistrationVerifyCodeView(CustomView):
    form_class = VerifyCodeForm
    template_name = 'accounts/verifycode.html'
    context = {
        'form': form_class
    }
    http_method_names = ['get', 'post']

    def get(self, request):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        user_session = request.session['user_registration_info']
        code_instance = OptCode.objects.get(phone_number=user_session['phone_number'])
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            deatht_time = code_instance.created + timezone.timedelta(minutes=2)

            if cd['code'] == code_instance.code and deatht_time > datetime.now(tz=pytz.timezone('Asia/Tehran')):
                User.objects.create_user(
                    phone_number=user_session['phone_number'],
                    email=user_session['email'],
                    username=user_session['username'],
                    password=user_session['password'],
                )

                code_instance.delete()
                messages.success(request, 'User created successfully', extra_tags='success')
                return redirect('home')
            else:
                messages.error(request, 'Wrong code!!', extra_tags='error')
                return redirect('verify_code')


class UserChangeView(CustomView):
    """
    View for changing user information.
    """
    form_class = CustomUserChangeForm
    template_name = 'accounts/change_user.html'
    success_url = reverse_lazy('home')
    http_method_names = ['get', 'post']

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.user_instance = self.request.user  # noqa

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to display the user change form.
        """
        user = self.user_instance
        form = self.form_class(instance=user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to process form submission for changing user information.
        """
        user = self.user_instance
        form = self.form_class(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User information updated successfully', extra_tags='success')
            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form})


class ChangePasswordView(CustomView):
    """
    This class defines a view for changing user password.

    Attributes:
        template_name (str): The name of the template to be rendered.
        form_class (class): The form class to be used.

    Methods:
        get: Method to handle GET requests.
        post: Method to handle POST requests for changing password.
    """

    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('home')
    http_method_names = ['get', 'post']
    form_class = ChangePasswordForm

    def get(self, request):
        """
        Method to handle GET requests.

        Args:
            request: The HTTP GET request object.

        Returns:
            HttpResponse: The HTTP response object.
        """
        form = self.form_class(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        Method to handle POST requests for changing password.

        Args:
            request: The HTTP POST request object.

        Returns:
            HttpResponse: The HTTP response object.
        """
        form = self.form_class(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect(reverse('home'))
        return render(request, self.template_name, {'form': form})


class UserPasswordResetView(PasswordResetView):
    template_name = 'accounts/email/password_reset.html'
    success_url = reverse_lazy('resat_done')
    form_class = UserPasswordResetForm
    http_method_names = ['get', 'post']
    email_template_name = 'accounts/email/password_reset_email.html'


class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/email/password_resat_done.html'
    http_method_names = ['get']


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/email/password_reset_confirm.html'
    success_url = reverse_lazy('resat_complete')
    http_method_names = ['get', 'post']


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/email/password_reset_complete.html'
    http_method_names = ['get']


class CreateProfileView(CustomView):
    """
    Handles user profile creation.
    """
    template_name = 'accounts/create_profile.html'
    http_method_names = ['get', 'post']
    form_class = ProfileChangeOrCreationForm

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
            return redirect('home')
        else:
            messages.error(
                request,
                'Your profile has not been created successfully',
                extra_tags='error')
            return redirect('create_profile')


class ProfileDetailView(DetailView):
    """
    Displays user profile details.
    """
    model = Profile
    template_name = 'accounts/profile_detail.html'
    context_object_name = 'profile'
    http_method_names = ['get']

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
    model = Profile
    success_url = reverse_lazy('home')
    template_name = 'accounts/delete_account.html'
    http_method_names = ['get', 'post']

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
    model = User
    template_name = 'accounts/delete_user.html'
    success_url = reverse_lazy('home')

    def delete(self, request, *args, **kwargs):
        """
        Handle soft deletion of the user.
        """
        self.object = self.get_object()  # noqa
        success_url = self.get_success_url()
        self.object.soft_delete.filter(pk=self.object.pk).delete()
        messages.success(request, 'User has been successfully deleted.')
        return redirect(success_url)
