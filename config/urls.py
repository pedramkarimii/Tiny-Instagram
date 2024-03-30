from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

"""
Defines URL patterns for the entire Django project.
- The 'admin/' URL pattern is associated with the Django admin interface.
- URL patterns for the 'account', 'post', and 'core' apps are included using the include() function.
- Static files serving is configured using the static() function to serve media files during development.
- Customizes the Django admin interface with a custom header, title, and index title.
These URL patterns define the structure of the web application and route requests to appropriate views.
"""
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app.account.urls")),
    path("", include("app.post.urls")),
    path("", include("app.core.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""
Customizes the Django admin site header, title, and index title.
"""
admin.site.site_header = 'Social Media'
admin.site.site_title = 'Social Media Administration'
admin.site.index_title = 'Welcome To Social Media Administration'
