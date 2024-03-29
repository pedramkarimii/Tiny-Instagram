from django.contrib.auth.forms import ReadOnlyPasswordHashField, PasswordChangeForm, PasswordResetForm
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.forms.widgets import TextInput, Select
from ckeditor.widgets import CKEditorWidget
from account.models import User, Profile, OptCode
from django import forms
import re


class CleanPassword(forms.Form):
    def clean_password(self):
        """
        Clean and validate the confirmation password field.
        Raises:
            forms.ValidationError: If the passwords don't match or if the password fails the specified criteria.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+])[A-Za-z\d!@#$%^&*()_+]{8,}$"
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        elif not re.match(pattern, password):
            raise forms.ValidationError(
                "Password must contain at least one uppercase letter, one lowercase letter, one digit,"
                " and one special character.")
        elif ' ' in password:
            raise forms.ValidationError("Password cannot contain spaces.")

        return password


class UserLoginForm(CleanPassword):
    """Defines a form for user login using phone number and password.
    This form allows users to log in using their phone number and password.
    """
    phone_number = forms.CharField(label='Phone Number', max_length=11)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean_phone_number(self):
        """
        Clean and validate the phone number field.

        Raises:
            forms.ValidationError: If the phone number is already registered.
        """

        phone_number = self.cleaned_data['phone_number']  # noqa
        OptCode.objects.filter(phone_number=phone_number).delete()
        pattern = r"09(1[0-9]|3[0-9]|2[0-9]|0[1-9]|9[0-9])[0-9]{7}$"
        if not re.match(pattern, phone_number):
            raise forms.ValidationError("Invalid phone number or password.")
        user = User.objects.get(phone_number=phone_number)
        if user:
            return phone_number

    def clean(self):
        """
        Customizes the data cleaning process for the form.
        Validates the phone number and password combination.
        Raises a validation error if the phone number or password is invalid.
        """

        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')
        password = cleaned_data.get('password')
        if phone_number and password:
            user = User.objects.get(phone_number=phone_number)
            if not user:
                raise forms.ValidationError("Invalid phone number or password.")
            if not check_password(password, user.password):
                raise forms.ValidationError("Invalid phone number or password.")

        return cleaned_data


class UserLoginEmailForm(CleanPassword):
    """Defines a form for user login using email and password.
    This form allows users to log in using their email address and password.
    """

    email = forms.EmailField(label='Email', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean_email(self):
        """
        Clean and validate the email field.

        Raises:
            forms.ValidationError: If the email address is already registered,
                doesn't end with '@gmail.com' or '@yahoo.com',
                doesn't contain '@', contains spaces, is empty, longer than 254 characters, or doesn't end with '.com'.
        """
        email = self.cleaned_data['email']
        email_pattern = r'^[a-zA-Z0-9._%+-]+@(?:gmail|yahoo)\.com$'
        user = User.objects.get(email=email)
        if not re.match(email_pattern, email):
            raise forms.ValidationError("Please enter a valid gmail or yahoo email address.")
        elif ' ' in email:
            raise forms.ValidationError("Email address cannot contain spaces.")
        if user:
            return email

    def clean(self):
        """
        Customizes the data cleaning process for the form.
        Validates the email and password combination.
        Raises a validation error if the email or password is invalid.
        """

        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = User.objects.get(email=email)
            if not user:
                raise forms.ValidationError("Invalid email or password.")

            if not check_password(password, user.password):
                raise forms.ValidationError("Invalid email or password.")

        return cleaned_data


class CleanDataUserForm(forms.ModelForm):
    """
    This class defines a custom user creation form with additional data cleaning and validation methods.

    Attributes:
        email (forms.EmailField): Field for entering email address.
        username (forms.CharField): Field for entering username.
        phone_number (forms.CharField): Field for entering phone number.
        password1 (forms.CharField): Field for entering password.
        password2 (forms.CharField): Field for confirming password.

    Methods:
        clean_email: Method to clean and validate the email field.
        clean_username: Method to clean and validate the username field.
        clean_phone_number: Method to clean and validate the phone number field.
    """
    email = forms.EmailField(label='Email', max_length=100)
    username = forms.CharField(label='Username', max_length=100)
    phone_number = forms.CharField(label='Phone Number', max_length=11)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Username',
            'email': 'Email',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }
        help_texts = {
            'username': 'Enter a unique username',
            'email': 'Enter your email address',
        }
        error_messages = {
            'username': {
                'required': 'Username is required',
                'unique': 'Username already exists',
            },
            'email': {
                'required': 'Email is required',
                'unique': 'Email already exists',
            },
        }

    def clean_email(self):
        """
        Clean and validate the email field.

        Raises:
            forms.ValidationError: If the email address is already registered,
                doesn't end with '@gmail.com' or '@yahoo.com',
                doesn't contain '@', contains spaces, is empty, longer than 254 characters, or doesn't end with '.com'.
        """
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email).exists()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@(?:gmail|yahoo)\.com$'

        if user:
            raise forms.ValidationError("This email address is already registered.")
        if not re.match(email_pattern, email):
            raise forms.ValidationError("Please enter a valid gmail or yahoo email address.")
        elif ' ' in email:
            raise forms.ValidationError("Email address cannot contain spaces.")
        return email

    def clean_username(self):
        """
        Clean and validate the username field.

        Raises:
            forms.ValidationError: If the username is already registered, less than 4 characters long,
                or if it contains invalid characters.
        """
        username = self.cleaned_data['username']
        user = User.objects.filter(username=username).exists()
        username_pattern = r'^[A-Za-z0-9@#_$%^&*()-+=]{4,26}$'

        if user:
            raise forms.ValidationError("This username is already registered.")
        elif not re.match(username_pattern, username):
            raise forms.ValidationError(
                "Username must contain only letters, digits, or underscores and be at least 4 characters long.")
        return username

    def clean_phone_number(self):
        """
        Clean and validate the phone number field.

        Raises:
            forms.ValidationError: If the phone number is already registered.
        """

        phone_number = self.cleaned_data['phone_number']
        OptCode.objects.filter(phone_number=phone_number).delete()
        pattern = r"09(1[0-9]|3[0-9]|2[0-9]|0[1-9]|9[0-9])[0-9]{7}$"
        if not re.match(pattern, phone_number):
            raise forms.ValidationError("Please enter a valid phone number.")
        user = User.objects.filter(phone_number=phone_number).exists()
        if user:
            raise forms.ValidationError("This phone number address is already registered.")

        return phone_number

    def clean_password2(self):
        """
        Clean and validate the confirmation password field.

        Raises:
            forms.ValidationError: If the passwords don't match or if the password fails the specified criteria.
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+])[A-Za-z\d!@#$%^&*()_+]{8,}$"

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        elif len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        elif not re.match(pattern, password1):
            raise forms.ValidationError(
                "Password must contain at least one uppercase letter, one lowercase letter, one digit,"
                " and one special character.")
        elif ' ' in password1:
            raise forms.ValidationError("Password cannot contain spaces.")

        return password2


class UserRegistrationForm(CleanDataUserForm):
    """
    This class defines a form for user registration, extending the CleanDataUserForm.

    Attributes:
        inheritance CleanDataUserForm

    Methods:
        __init__: Constructor method to initialize form fields.
        save: Method to save the created user as a regular user.
    """

    def save(self, commit=True):
        """
        Save the created user as a regular user.

        Args:
            commit (bool, optional): Indicates whether to save the user to the database. Defaults to True.

        Returns:
            User: The created user instance.
        """
        user = super().save(commit=False)
        user.is_staff = False
        user.is_admin = False
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    This class defines a form for changing user information.

    Attributes:
        password (ReadOnlyPasswordHashField): Field for displaying password, with a link to change it.
    """

    password = ReadOnlyPasswordHashField(
        help_text="You can change using password <a href=\"../password\">this form</a>")

    class Meta:
        model = User
        fields = ('email', 'phone_number', 'username', 'password', 'last_login')
        labels = {
            'email': 'Email',
            'phone_number': 'Phone Number',
            'username': 'Username',
        }
        help_texts = {
            'email': 'Enter your email',
            'phone_number': 'Enter your phone number',
            'username': 'Enter your username',
        }
        error_messages = {
            'email': {
                'required': 'Email is required',
                'invalid': 'Invalid email format',
            },
            'phone_number': {
                'required': 'Phone number is required',
                'invalid': 'Invalid phone number format',
            },
            'username': {
                'required': 'Username is required',
                'invalid': 'Invalid username format'},
        }


class ChangePasswordForm(PasswordChangeForm):
    """
    This class defines a form for changing user password, extending the PasswordChangeForm.

    Methods:
        __init__: Constructor method to customize form field widgets.
        clean_new_password1: Custom validation method to check password similarity and additional rules.
    """

    old_password = forms.CharField(label="Old Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label="New Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label="Confirm New Password",
                                    widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        """
        Constructor method to customize form field widgets.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        for password in ['old_password', 'new_password1', 'new_password2']:
            self.fields[password].widget.attrs.update({'class': 'form-control'})

    def clean_new_password1(self):
        """
        Clean the new password and ensure it meets complexity requirements.
        """
        new_password1 = self.cleaned_data.get('new_password1')
        old_password = self.cleaned_data.get('old_password')
        username = self.user.username if self.user else None

        if new_password1 and old_password and new_password1 == old_password:
            raise ValidationError("The new password must be different from the old password.")

        if username and new_password1 and username in new_password1:
            raise ValidationError("The password cannot be too similar to the username.")

        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+])[A-Za-z\d!@#$%^&*()_+]{8,}$"

        if len(new_password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        elif not re.match(pattern, new_password1):
            raise ValidationError(
                "Password must contain at least one uppercase letter, one lowercase letter, one digit,"
                " and one special character.")
        elif ' ' in new_password1:
            raise ValidationError("Password cannot contain spaces.")
        if username and new_password1 and new_password1.lower().startswith(username.lower()):
            return new_password1
        return new_password1


class UserPasswordResetForm(PasswordResetForm):
    """
    This class defines a form for resetting user password, extending the PasswordResetForm.

    Methods:
        __init__: Constructor method to customize form field widgets.

    """

    def __init__(self, *args, **kwargs):
        """
        Constructor method to customize form field widgets.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        for password in ['email']:
            self.fields[password].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = User
        fields = ('email',)


class CustomUserChangeForm(forms.ModelForm):
    """
    This class defines a custom user change form, extending the UserChangeForm.
    """

    class Meta:
        """
        Meta class to specify the model and fields for the form.
        """
        model = User
        fields = ['username', 'email', 'phone_number']


class ProfileForm(forms.ModelForm):
    """
    This class defines a form for user profile information.
    """

    class Meta:
        """
        Meta class to specify the model and fields for the form, along with widget attributes,
        labels, help texts, and error messages.
        """
        model = Profile
        fields = ('full_name', 'name', 'last_name', 'age', 'gender', 'bio', 'profile_picture')
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'full_name': 'Full Name',
            'name': 'Name',
            'last_name': 'Last Name',
            'age': 'Age',
            'gender': 'Gender',
            'bio': 'Bio',
            'profile_picture': 'Profile Picture',
        }
        help_texts = {
            'full_name': 'Enter your full name',
            'name': 'Enter your name',
            'last_name': 'Enter your last name',
            'age': 'Enter your age',
            'gender': 'Select your gender',
            'bio': 'Enter your bio',
            'profile_picture': 'Upload your profile picture',
        }
        error_messages = {
            'full_name': {
                'required': 'Full name is required',
                'invalid': 'Invalid full name format',
            },
            'name': {
                'required': 'Name is required',
                'invalid': 'Invalid name format',
            },

            'last_name': {
                'required': 'Last name is required',
                'invalid': 'Invalid last name format',
            },

            'age': {
                'required': 'Age is required',
                'invalid': 'Invalid age format',
                'min_value': 'Age must be at least 18',
            },
            'gender': {
                'required': 'Gender is required',
                'invalid': 'Invalid gender format',
            },
            'bio': {
                'required': 'Bio is required',
                'invalid': 'Invalid bio format',
            },
            'profile_picture': {
                'required': 'Profile picture is required',
                'invalid': 'Invalid profile picture format',
            },

        }


class ProfileChangeOrCreationForm(forms.ModelForm):
    """
    This class defines a form for changing or creating user profile information.

    Methods:
         profile_picture: Method to handle profile picture upload.
        clean_age: Method to clean and validate the age field.
        clean_gender: Method to clean and validate the gender field.
        save: Method to save the changes made in the form.

    """
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )

    full_name = forms.CharField(label='Full Name', required=False, widget=TextInput(attrs={
        'class': 'mt-1 pt-2 py-2 px-4 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm'
                 ' border-gray-300 rounded-md'}))
    name = forms.CharField(label='Name', required=False, widget=TextInput(attrs={
        'class': 'mt-1 pt-2 py-2 px-4 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm'
                 ' border-gray-300 rounded-md'}))
    last_name = forms.CharField(label='Last Name', required=False, widget=TextInput(attrs={
        'class': 'mt-1 pt-2 py-2 px-4 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm'
                 ' border-gray-300 rounded-md'}))
    age = forms.IntegerField(label='Age', required=False, widget=forms.NumberInput(attrs={
        'class': 'mt-1 pt-2 py-2 px-4 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm'
                 ' border-gray-300 rounded-md',
        'min': '18'}))
    gender = forms.ChoiceField(label='Gender', choices=GENDER_CHOICES, widget=Select(attrs={
        'class': 'mt-1 pt-2 py-2 px-4 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm'
                 ' border-gray-300 rounded-md'}))
    bio = forms.CharField(label='Bio',
                          required=False, widget=CKEditorWidget(attrs={'class': 'mt-1 pt-2 py-2 px-4 '
                                                                                'focus:ring-indigo-500 '
                                                                                'focus:border-indigo-500 block w-full '
                                                                                'shadow-sm sm:text-sm border-gray-300 '
                                                                                'rounded-md'}))
    profile_picture = forms.ImageField(label='Profile Picture', required=False,
                                       widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        """
        Meta class to specify the model and fields for the form.
        """
        model = Profile
        fields = ('full_name', 'name', 'last_name', 'age', 'gender', 'bio', 'profile_picture')

    def __init__(self, *args, **kwargs):
        """
        Constructor method to initialize form fields.
        """
        super(ProfileChangeOrCreationForm, self).__init__(*args, **kwargs)
        self.fields['age'].widget.attrs['min'] = 18
        self.fields['profile_picture'].widget.attrs['accept'] = 'image/*'

    def profile_bio(self, user_id, bio_text):  # noqa
        """
        Method to handle updating user's bio.

        Args:
            user_id (int): The ID of the user whose bio is being updated.
            bio_text (str): The new bio text.

        Returns:
            Profile: The updated profile instance.
        """
        profile = Profile.objects.get(user_id=user_id)
        profile.bio = bio_text
        profile.save()
        return profile

    def profile_pictures(self, user_id, commit=True):
        """
        Method to handle profile picture upload.

        Args:
            user_id (int): The ID of the user for whom the profile picture is uploaded.
            commit (bool, optional): Indicates whether to save the profile to the database. Defaults to True.

        Returns:
            Profile: The profile instance with the updated profile picture.
        """
        profile = Profile.objects.get(user_id=user_id)
        if 'profile_picture' in self.files:
            profile.profile_picture = self.files['profile_picture']
            if commit:
                profile.save()

        return profile

    def clean_age(self):
        """
        Clean and validate the age field.

        Returns:
            int: Cleaned and validated age value.

        Raises:
            forms.ValidationError: If age is less than 18.
        """
        age = self.cleaned_data.get('age')
        if age < 18:
            raise forms.ValidationError("Age must be at least 18.")
        return age

    def clean_gender(self):
        """
        Clean and validate the gender field.

        Returns:
            str: Cleaned and validated gender value.

        Raises:
            forms.ValidationError: If an invalid gender selection is made.
        """
        gender = self.cleaned_data.get('gender')

        if gender not in ['male', 'female']:
            raise forms.ValidationError("Invalid gender selection.")
        return gender

    def save(self, commit=True):
        """
        Save the changes made in the form.

        Args:
            commit (bool, optional): Indicates whether to save the user to the database. Defaults to True.

        Returns:
            User: The user instance with the changes made in the form.
        """
        user = super(ProfileChangeOrCreationForm, self).save(commit=False)
        if commit:
            user.save()
        return user


class VerifyCodeForm(forms.Form):
    """
    This class defines a form for verifying a code.

    Methods:
        clean_code: Method to clean and validate the code field.

    """
    code = forms.IntegerField(label='Code', min_value=1000, max_value=9999,
                              widget=forms.NumberInput(attrs={'autocomplete': 'off'}))

    def clean_code(self):
        """
        Clean and validate the code field.

        Returns:
            int: Cleaned and validated code value.

        Raises:
            forms.ValidationError: If the code is not a 6-digit number.
        """
        code = self.cleaned_data['code']
        if code < 1000 or code > 9999:
            raise forms.ValidationError("Code must be a 4-digit number.")
        return code
