from itertools import count
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.conf import settings
from django.templatetags.static import static
from django.contrib import messages
from django.forms import modelformset_factory
from django.db.models import Count, Sum
from django.utils import timezone

import datetime
from taggit.models import Tag
from star_ratings.models import Rating, RatingManager

from decimal import Decimal
import os
from .models import *
from .forms import *
from users.models import Profile


def ProjectsFormView(request):    
    ImageFormSet = modelformset_factory(ProjectPictures, form=ProjectPictureForm, extra=4)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)        
        formset = ImageFormSet(request.POST, request.FILES,queryset=ProjectPictures.objects.none())
        if form.is_valid() and formset.is_valid():
            new = form.save(commit=False)   
            new.owner = request.user    
            new.save()
            form.save_m2m()
            for picform in formset.cleaned_data:
                # this helps to not crash if the user
                # do not upload all the photos
                if picform:
                    image = picform['picture']
                    photo = ProjectPictures(project_id=form,picture_label=form.cleaned_data.get('title') ,picture=image)
                    photo.save()
            return redirect('create_project')
        else:
            print("Not Valid")
            print(form.errors)
            #print(form.get("book_image"))
            return render(request, 'crapp/addproject.html',{'form':form, 'formset': formset})
    else:
        form = ProjectForm()
        formset = ImageFormSet(queryset=ProjectPictures.objects.none())
        return render(request, 'crapp/addproject.html',{'form':form, 'formset': formset})

def ProjectsFormExtendView(request):        
    if request.method == 'POST':
        form = ProjectFormExtend(request.POST, request.FILES)       
        files = request.FILES.getlist('images') 

        if form.is_valid():
            new = form.save(commit=False)   
            new.owner = request.user    
            new.save()
            form.save_m2m()
            for f in files:
                ProjectPictures.objects.create(project_id=new, picture_label=form.cleaned_data.get('title'), picture=f)
                
            return redirect('create_project')
        else:
            print("Not Valid")
            print(form.errors)
            #print(form.get("book_image"))
            return render(request, 'crapp/addproject.html',{'form':form})
    else:
        form = ProjectFormExtend()
        return render(request, 'crapp/addproject.html',{'form':form})

def CategoreyFormView(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            new = form.save(commit=False)       
            new.save()
            return redirect('categorey')
        else:
            print("Not Valid")
            print(form.errors)
            #print(form.get("book_image"))
            return render(request, 'crapp/categorey.html',{'form':form})
    else:
        cats = Category.objects.all()
        form = CategoryForm()
        context = {"cats": cats,'form': form}
        return render(request, "crapp/categorey.html", context)

def All_Projects(request):
    allprojects = Projects.objects.all()
    print(allprojects)
    context = {"allprojects": allprojects}
    return render(request, "crapp/projects.html", context)

def ProjectDetails(request,id):
    projectc = get_object_or_404(Projects, id=id)
    project = Projects.objects.filter(id=id).all()    
    images = ProjectPictures.objects.filter(project_id=id).all()    
    donations = DonationFund.objects.filter(project=id).all()
    tags = Projects.tags.all()
    similarprojects = projectc.tags.similar_objects()
    donatorcount = DonationFund.objects.filter(project=id).all().annotate(count=Count('donator'))
    totalfund = DonationFund.objects.filter(project=id).all().aggregate(Sum('amount'))['amount__sum']
    myuser = get_object_or_404(Profile, user_id=request.user.id)    
    context = {"myuser":myuser, "project":project, "images":images, "donations": donations, "tags": tags, "donatorcount": donatorcount, "totalfund": totalfund, "similarprojects": similarprojects[:5]}
    if request.method == 'POST':
        amount = request.POST.get('donateammount')
        print(amount)
        return redirect('donate', id , amount)
    return render(request, "crapp/projectdetails.html", context)

def Donate(request, id, amount):
    project = get_object_or_404(Projects, id= id)
    context = {"project": project}
    #if request.method == "POST":
     #amount = request.POST.get('amount')
    print("Hello")
    # validate
    if amount:
        #price_in_decimal = Decimal(amount)
        #print(price_in_decimal)
        if project.end_date > timezone.now():
            prev_donations = DonationFund.objects.filter(project=id, donator=request.user.id)
            print(prev_donations)
            # has donated for this campaign before
            if prev_donations:

                prev_donations[0].amount += int(amount)
                prev_donations[0].save()

            # first time
            else:
                DonationFund.objects.create(
                    amount=amount, project=project, donator=request.user)
        return redirect('projectdetails', id)

    else:
        messages.error(request, 'Invalid amount')

    return redirect('projectdetails', id)

def ProjectReport(request, id):
    project = get_object_or_404(Projects, id=id)
    if request.method == 'POST':
        form = ProjectReportsForm(request.POST)

        if form.is_valid():
            new = form.save(commit=False) 
            new.reporter = request.user  
            new.project = project  
            new.save()
            return redirect('projects')
        else:
            print("Not Valid")
            print(form.errors)
            #print(form.get("book_image"))
            return render(request, 'crapp/projectreports.html',{'form':form})
    else:
        form = ProjectReportsForm()
        context = {"project": project,'form': form}
        return render(request, "crapp/projectreports.html", context)

def home(request):
    myuser = get_object_or_404(Profile, user_id=request.user.id)    
    topprojects = Projects.objects.filter(ratings__isnull=False).order_by('ratings__average')
    lastprojects = Projects.objects.all().order_by('creation_date')
    featuredprojects =  Projects.objects.filter(ratings__isnull=False, is_featured=True).order_by('ratings__average')
    cats = Category.objects.all()
    context = {"myuser":myuser, "topprojects": topprojects[:5], "lastprojects":lastprojects[:5], "featuredprojects":featuredprojects[:5],"cats":cats}
    return render(request, "crapp/home.html", context)

def CategoreyProjectView(request, id):
    cats = Category.objects.filter(c_id=id).all()
    projects = Projects.objects.filter(category=id).all()
    context = {"cats": cats, "projects": projects}
    return render(request, "crapp/categoreyprojects.html", context)

def UserProjects(request):
    projects = Projects.objects.filter(owner=request.user).all()
    myuser = get_object_or_404(Profile, user_id=request.user.id)    
    context = {"projects":projects, "myuser":myuser}
    return render(request, "crapp/userprojects.html", context)

def UserDonation(request):
    donation = DonationFund.objects.filter(donator=request.user).all()
    myuser = get_object_or_404(Profile, user_id=request.user.id) 
    context = {"donation":donation, "myuser":myuser}
    return render(request, "crapp/userdonate.html", context)
    