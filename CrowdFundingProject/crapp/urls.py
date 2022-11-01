from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from . import views

urlpatterns = [
    path('comment/', include('comment.urls')),
    path('ratings/', include('star_ratings.urls', namespace='ratings')),
    path('home/', views.home, name="home"),
    path('addproject/', views.ProjectsFormExtendView, name="create_project"),
    path('projects/', views.All_Projects, name="projects"),
    path('categorey/', views.CategoreyFormView, name="categorey"),
    path('userprojects/', views.UserProjects, name="userprojects"),
    path('userdonate/', views.UserDonation, name="userdonate"),
    path('projectdetails/<int:id>', views.ProjectDetails, name='projectdetails'),
    path('editproject/<int:id>', views.EditProject, name='editproject'),
    path('donate/<int:id>/<amount>', views.Donate, name='donate'),
    path('projectreports/<int:id>', views.ProjectReport, name='projectreports'),
    path('catprojects/<int:id>', views.CategoreyProjectView, name='catprojects'),
    path('cancelproject/<int:id>', views.CancelProject, name='cancelproject'),
    path('search/<str:search>', views.search, name='search'),
    
    #path('', TemplateView.as_view(template_name='crowdfunding/home.html'), name='home'), # new

] 