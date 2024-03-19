from django.contrib import messages
from django.db import models
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View


class SoftDeleteMixin(models.QuerySet):
    def delete(self):
        """
        Soft delete objects in the queryset.

        Instead of permanently deleting objects from the database,
        mark them as deleted by setting the 'is_deleted' field to True.
        """
        return super().update(is_deleted=True, is_active=False)


class DeleteManagerMixin(models.Manager):

    def get_queryset_object(self):
        """
        Get the queryset object associated with this manager.

        If the queryset object has not been created yet, create it
        using ManagerQuerySetDelete to handle soft deletion.
        """
        if not hasattr(self.__class__, '__queryset'):
            self.__class__.__queryset = SoftDeleteMixin(self.model)
        return self.__queryset

    def get_queryset(self):
        """
        Get the filtered queryset, excluding deleted and inactive objects.

        This method filters out objects marked as deleted ('is_deleted'=True)
        and inactive ('is_active'=False) from the queryset.
        """
        return self.get_queryset_object().filter(is_active=True, is_deleted=False)

    def archive(self):
        """
        Retrieve all objects, including deleted and inactive ones.

        This method returns all objects in the queryset, including those
        marked as deleted or inactive. It is provided as an alias for
        get_queryset() but may be redundant in most use cases.
        """
        return super().get_queryset()


class HttpsOptionNotLogoutMixin(View):
    def setup(self, request, *args, **kwargs):  # noqa
        """Initialize the next_page_create_profile, get profile, authenticate."""
        self.next_page_home = reverse_lazy('home')  # noqa
        self.template_http_method_not_allowed = 'base/http_method_not_allowed.html'  # noqa
        self.authenticate = request.user.is_authenticated  # noqa
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch method to handle user authentication status.
        Redirects non-authenticated users to the home page with an error message.
        """
        if not self.authenticate:
            messages.error(
                request,
                'You are not login please first login your account.',
                extra_tags='error',
            )
            return redirect(self.next_page_home)
        else:
            return super().dispatch(request, *args, **kwargs)

    def options(self, request, *args, **kwargs):
        """
        Handles OPTIONS requests.
        Returns a response with the allowed HTTP methods.
        """
        response = super().options(request, *args, **kwargs)
        response.headers['host'] = 'localhost'
        return response

    def http_method_not_allowed(self, request, *args, **kwargs):
        """
        Handles HTTP method not allowed requests.
        Returns a response with the allowed HTTP methods.
        This method is called when a request is made with an unsupported HTTP method.
        """
        super().http_method_not_allowed(request, *args, **kwargs)
        return render(request, self.template_http_method_not_allowed)


class HttpsOptionLoginMixin(View):
    def setup(self, request, *args, **kwargs):  # noqa
        """Initialize the next_page_create_profile, get profile, authenticate."""
        self.next_page_home = reverse_lazy('home')  # noqa
        self.template_http_method_not_allowed = 'base/http_method_not_allowed.html'  # noqa
        self.authenticate = request.user.is_authenticated  # noqa
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch method to handle user authentication status.
        If the user is authenticated, redirect to the home page.
        Otherwise, proceed with the default dispatch behavior.
        """
        if self.authenticate:
            messages.warning(request, 'You are already login.', extra_tags='warning')
            return redirect(self.next_page_home)

        else:
            return super().dispatch(request, *args, **kwargs)

    def options(self, request, *args, **kwargs):
        """
        Handles OPTIONS requests.
        Returns a response with the allowed HTTP methods.
        """
        response = super().options(request, *args, **kwargs)
        response.headers['host'] = 'localhost'
        return response

    def http_method_not_allowed(self, request, *args, **kwargs):
        """
        Handles HTTP method not allowed requests.
        Returns a response with the allowed HTTP methods.
        This method is called when a request is made with an unsupported HTTP method.
        """
        super().http_method_not_allowed(request, *args, **kwargs)
        return render(request, self.template_http_method_not_allowed)
