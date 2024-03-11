from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name='base/bases.html'), name="home"),
    path("", include("account.urls")),
    path("", include("post.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
admin.site.site_header = 'Social Media'
admin.site.site_title = 'Social Media Administration'
admin.site.index_title = 'Welcome To Social Media Administration'
