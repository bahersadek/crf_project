from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path('', TemplateView.as_view(template_name='crowdfunding/home.html'), name='home'), # new

]