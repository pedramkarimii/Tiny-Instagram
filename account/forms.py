from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField, PasswordChangeForm, UserCreationForm
from account.models import User, OptCode, Profile
from django import forms


class CleanDataUserForm(UserCreationForm):
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
    email = forms.EmailField(label='Email', max_length=254)
    username = forms.CharField(label='Username', max_length=100)
    phone_number = forms.CharField(label='Phone Number', max_length=11)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
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
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        elif not email.endswith('@gmail.com') or email.endswith('@yahoo.com'):
            raise forms.ValidationError("Please use a gmail address.")
        elif '@' not in email:
            raise forms.ValidationError("Please enter a valid email address.")
        elif ' ' in email:
            raise forms.ValidationError("Email address cannot contain spaces.")
        elif len(email) < 1:
            raise forms.ValidationError("Email address must be at least 1 characters long.")
        elif len(email) > 254:
            raise forms.ValidationError("Email address cannot be longer than 254 characters.")
        elif not email.endswith('.com'):
            raise forms.ValidationError("Please enter a valid email address.")
        return email

    def clean_username(self):
        """
        Clean and validate the username field.

        Raises:
            forms.ValidationError: If the username is already registered, less than 5 characters long,
             or longer than 150 characters.
        """
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username address is already registered.")
        elif len(username) < 5:
            raise forms.ValidationError("Username must be at least 5 characters long.")
        return username

    def clean_phone_number(self):
        """
        Clean and validate the phone number field.

        Raises:
            forms.ValidationError: If the phone number is already registered.
        """
        phone_number = self.cleaned_data['phone_number']
        OptCode.objects.filter(phone_number=phone_number).delete()
        if User.objects.filter(phone_number=phone_number).exists():
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
        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")
        elif len(password1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        elif password1.isalpha() or password1.isdigit():
            raise forms.ValidationError("Password must contain at least one letter and one number.")
        elif not any(char.isdigit() for char in password1):
            raise forms.ValidationError("Password must contain at least one number.")
        elif not any(char.isalpha() for char in password1):
            raise forms.ValidationError("Password must contain at least one letter.")
        elif not any(char.isupper() for char in password1):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        elif not any(char.islower() for char in password1):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        elif not any(char in '!@#$%^&*()_+' for char in password1):
            raise forms.ValidationError("Password must contain at least one special character.")
        elif ' ' in password1:
            raise forms.ValidationError("Password cannot contain spaces.")
        return password2


class AdminCreationForm(CleanDataUserForm):
    """
    This class defines a form for creating admin users, extending the CleanDataUserForm.

    Methods:
        save: Method to save the created user as an admin user.

    Attributes:
        Constructor method to initialize form fields.
        Method to save the created user as a regular user.
    """

    def save(self, commit=True):
        """
        Save the created user as an admin user.

        Args:
            commit (bool, optional): Indicates whether to save the user to the database. Defaults to True.

        Returns:
            User: The created user instance.
        """
        user = super().save(commit=False)
        user.is_staff = True
        user.is_admin = True
        if commit:
            user.save()
        return user


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
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
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

    """

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

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')


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
    full_name = forms.CharField(label='Full Name', required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    name = forms.CharField(label='Name', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Last Name', required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    age = forms.IntegerField(label='Age', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    gender = forms.ChoiceField(label='Gender', required=False, choices=[('M', 'Male'), ('F', 'Female')],
                               widget=forms.Select(attrs={'class': 'form-control'}))
    bio = RichTextField(config_name='default', )
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
        # Retrieve the user's profile
        profile = Profile.objects.get(user_id=user_id)

        # Check if the form has a profile picture file attached
        if 'profile_picture' in self.files:
            # Assign the uploaded profile picture to the profile
            profile.profile_picture = self.files['profile_picture']

            # Save the profile if commit is True
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
        if gender not in ['M', 'F']:
            raise forms.ValidationError("Invalid gender selection.")
        elif gender == 'M':
            gender = 'Male'
            self.cleaned_data['gender'] = gender
            return gender
        elif gender == 'F':
            gender = 'Female'
            self.cleaned_data['gender'] = gender
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
