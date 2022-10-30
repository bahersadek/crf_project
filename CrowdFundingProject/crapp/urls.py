from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
    path('comment/', include('comment.urls')),
    path('ratings/', include('star_ratings.urls', namespace='ratings')),
    path('addproject/', views.ProjectsFormExtendView, name="create_project"),
    path('projects/', views.All_Projects, name="projects"),
    path('categorey/', views.CategoreyFormView, name="categorey"),
    path('projectdetails/<int:id>', views.ProjectDetails, name='projectdetails'),
    path('donate/<int:id>/<amount>', views.Donate, name='donate'),
    #path('', TemplateView.as_view(template_name='crowdfunding/home.html'), name='home'), # new

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)