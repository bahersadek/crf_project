from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
    path('dashboard',views.dashboard,name='dashboard'),
    path('register',views.register,name='register'),
    path("accounts/", include("django.contrib.auth.urls")),
    path('sent/', views.activation_sent_view, name="activation_sent"),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate, name='activate'),
    path('oauth/', include("social_django.urls")),
    #path('', TemplateView.as_view(template_name='crowdfunding/home.html'), name='home'), # new

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)