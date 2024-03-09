from django.db import models
from django.shortcuts import render
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


class HttpsOptionMixin(View):
    # def dispatch(self, request, *args, **kwargs):
    #     pass

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
        return render(request, 'base/http_method_not_allowed.html')
