from django.urls import path
from django.views.generic import TemplateView

from core.views import ContactUsView

"""
Defines URL patterns for the home, about us, and contact us pages.
- The root URL ('') is associated with a TemplateView displaying the 'bases.html' template, serving as the home page.
- The '/about_us/' URL pattern is associated with a TemplateView displaying the 'about_us.html' template, 
    representing the about us page.
- The '/contact_us/' URL pattern is associated with the ContactUs view, allowing users to access the contact us page.
These URL patterns define the navigation structure of the website, directing users to different pages.
"""

urlpatterns = [
    path("", TemplateView.as_view(template_name='home/home.html'), name="home"),
    path("about_us/", TemplateView.as_view(template_name='about_us/about_us.html'), name="about_us"),
    path('contact_us/', ContactUsView.as_view(), name='contact_us'),
]
