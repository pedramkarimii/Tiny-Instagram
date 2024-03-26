from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import View
from account.models import User
from .forms import ContactForm


class ContactUsView(View):
    """
   This class represents a view for handling a contact form submission.
   It provides methods to set up initial parameters, handle GET and POST requests,
   and process form submissions.
   Attributes:
       form_class (Form): The form class for the contact form.
       template_contact_us (str): The template name for the contact form.
       authenticate_user (bool): Indicates whether the user is authenticated.
       user (User): The authenticated user object.
       email_host_user (str): The email host user for sending emails.
       next_page_contact_us (str): The URL to redirect after form submission.
   """

    def setup(self, request, *args, **kwargs):
        """Set up initial parameters."""
        self.form_class = ContactForm  # noqa
        self.template_contact_us = 'contact_us/contact_us.html'  # noqa
        self.authenticate_user = request.user.is_authenticated  # noqa
        self.user = request.user  # noqa
        self.email_host_user = settings.EMAIL_HOST_USER  # noqa
        self.next_page_contact_us = reverse_lazy('contact_us')  # noqa
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Handle GET request."""
        return render(request, self.template_contact_us, {'form': self.form_class()})

    def post(self, request, *args, **kwargs):
        """
        Handle POST request.

        This method is responsible for processing the POST request when the user submits the contact form.
        It performs the following steps:

        1. Instantiates the contact form with the POST data.
        2. Checks if the form data is valid.
        3. Depending on whether the user is authenticated:
            a. If authenticated:
                - Retrieves the user object based on the provided email.
                - If the user exists, composes an email message with the form data, sends the email,
                  displays a success message, saves the form data, and redirects to the next page.
                - If the user does not exist, displays an error message and redirects to the next page.
            b. If not authenticated:
                - Caches the form data for later processing.
                - If successful, displays a success message and redirects to the next page.
                - If caching fails, displays an error message and redirects to the next page.
        4. If the form data is not valid, displays an error message and redirects to the next page.

        """
        form = self.form_class(request.POST)
        if form.is_valid():

            if self.authenticate_user:
                # Send email
                self.user = User.objects.get(email=form.cleaned_data['email'])  # noqa
                if self.user:
                    subject = 'New message from Tiny Instagram'
                    message = 'You have received a new message.\n\nName: {}\nEmail: {}\nMessage: {}'.format(
                        form.cleaned_data['name'],
                        form.cleaned_data['email'],
                        form.cleaned_data['message']
                    )
                    from_email = self.email_host_user
                    recipient_list = [form.cleaned_data['email']]
                    send_mail(subject, message, from_email, recipient_list)
                    messages.success(request, 'Your message has been sent successfully.')
                    form.save()
                    return redirect(self.next_page_contact_us)
                else:
                    messages.error(request, 'Please enter a valid gmail or yahoo email address')
                    return redirect(self.next_page_contact_us)
            else:
                try:
                    cache_key = f"contact_form_{form.cleaned_data['email']}"
                    cache.set(cache_key, form.cleaned_data, None)  # No timeout for caching
                    messages.success(request, 'Your message has been sent successfully.')
                    return redirect(self.next_page_contact_us)
                except Exception as e:
                    messages.error(request, f'Error caching form data: {e}')
                    return redirect(self.next_page_contact_us)
        else:
            messages.error(request, 'An error occurred while sending your message.')
            return redirect(self.next_page_contact_us)
