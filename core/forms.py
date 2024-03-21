from django import forms
import re


class ContactForm(forms.Form):
    """
    This ContactForm class is designed to validate and process user input from a contact form.
    Each field has its own validation rules implemented in the clean methods.
    The 'clean_name' method checks for spaces and length constraints on the name field.
    The 'clean_email' method validates the email format and ensures it belongs to Gmail or Yahoo domains.
    The 'clean_message' method checks for empty messages, length constraints, and filters out spam keywords.
    The 'save' method extracts cleaned data for further processing, such as sending emails or storing in a database.
    This class encapsulates form logic, promoting maintainability and code readability.
    """
    name = forms.CharField(label='Your Name', max_length=50)
    email = forms.EmailField(label='Your Email', max_length=255)
    message = forms.CharField(label='Message', widget=forms.Textarea)

    def clean_name(self):
        name = self.cleaned_data['name']
        if ' ' in name:
            raise forms.ValidationError("Name cannot contain spaces.")
        elif len(name) < 2:
            raise forms.ValidationError('name must be at least 3 characters long.')
        elif len(name) > 50:
            raise forms.ValidationError('name must be less than 200 characters long.')
        return name

    def clean_email(self):

        email = self.cleaned_data['email']
        email_pattern = r'^[a-zA-Z0-9._%+-]+@(?:gmail|yahoo)\.com$'
        if not re.match(email_pattern, email):
            raise forms.ValidationError("Please enter a valid gmail or yahoo email address.")
        elif ' ' in email:
            raise forms.ValidationError("Email address cannot contain spaces.")
        return email

    def clean_message(self):
        message = self.cleaned_data['message']
        if message.strip() == '':
            raise forms.ValidationError('Please enter a message.')
        elif len(message) < 3:
            raise forms.ValidationError('Message must be at least 3 characters long.')
        elif len(message) > 200:
            raise forms.ValidationError('Message must be less than 200 characters long.')
        if re.search(r'\b(spam|viagra)\b', message, flags=re.IGNORECASE):
            raise forms.ValidationError('Please avoid spam and viagra.')

        return message

    def save(self):
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        message = self.cleaned_data['message']
        return name, email, message
