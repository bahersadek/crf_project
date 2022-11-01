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
from django.contrib.auth.decorators import login_required

import datetime
from taggit.models import Tag
from star_ratings.models import Rating, RatingManager

from decimal import Decimal
import os
from .models import *
from .forms import *
from users.models import Profile

@login_required
def ProjectsFormView(request):    ###Old Formset Option
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

@login_required
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
                
            return redirect('projects')
        else:
            print("Not Valid")
            print(form.errors)
            #print(form.get("book_image"))
            return render(request, 'crapp/addproject.html',{'form':form})
    else:
        form = ProjectFormExtend()
        return render(request, 'crapp/addproject.html',{'form':form})

@login_required
def CategoreyFormView(request):
    myuser = get_object_or_404(Profile, user_id=request.user.id)    
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
            return render(request, 'crapp/categorey.html',{'form':form, "myuser": myuser})
    else:
        cats = Category.objects.all()
        form = CategoryForm()
        context = {"cats": cats,'form': form, "myuser":myuser}
        return render(request, "crapp/categorey.html", context)

@login_required
def All_Projects(request):
    myuser = get_object_or_404(Profile, user_id=request.user.id)    
    allprojects = projectsprogress() #Projects.objects.all()    
    print(allprojects)
    context = {"allprojects": allprojects, "myuser":myuser}
    return render(request, "crapp/projects.html", context)

@login_required
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
    context = {'now': datetime.datetime.now(), "myuser":myuser, "project":project, "images":images, "donations": donations, "tags": tags, "donatorcount": donatorcount, "totalfund": totalfund, "similarprojects": similarprojects[:5]}
    if request.method == 'POST':
        amount = request.POST.get('donateammount')
        print(amount)
        return redirect('donate', id , amount)
    return render(request, "crapp/projectdetails.html", context)

@login_required
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

@login_required
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

@login_required
def home(request):
    if request.method == "GET":
        myuser = get_object_or_404(Profile, user_id=request.user.id)    
        topprojects = Projects.objects.filter(ratings__isnull=False).order_by('ratings__average')
        lastprojects = Projects.objects.all().order_by('creation_date')
        featuredprojects =  Projects.objects.filter(ratings__isnull=False, is_featured=True).order_by('ratings__average')
        cats = Category.objects.all()
        context = {"myuser":myuser, "topprojects": topprojects[:5], "lastprojects":lastprojects[:5], "featuredprojects":featuredprojects[:5],"cats":cats}
        return render(request, "crapp/home.html", context)
    if request.method == "POST":
        search = request.POST.get('searchtext')
        return redirect('search', search)
        

@login_required
def CategoreyProjectView(request, id):
    cats = Category.objects.filter(c_id=id).all()
    myuser = get_object_or_404(Profile, user_id=request.user.id)    
    projects = projectsprogressbycat(id)#Projects.objects.filter(category=id).all()
    context = {"cats": cats, "projects": projects, "myuser":myuser}
    return render(request, "crapp/categoreyprojects.html", context)

@login_required
def UserProjects(request):
    projects = projectsprogressbyuser(request.user.id)#Projects.objects.filter(owner=request.user).all()
    myuser = get_object_or_404(Profile, user_id=request.user.id)    
    context = {"projects":projects, "myuser":myuser}
    return render(request, "crapp/userprojects.html", context)

@login_required
def UserDonation(request):
    donation = DonationFund.objects.filter(donator=request.user).all()
    myuser = get_object_or_404(Profile, user_id=request.user.id) 
    context = {"donation":donation, "myuser":myuser}
    return render(request, "crapp/userdonate.html", context)

def projectsprogress():
    sqlquery = ('SELECT t1.id, t1.title, t1.details, t1.target, t1.start_date, t1.end_date, t1.creation_date, '
               't1.is_featured, t1.category_id,t1.owner_id , round(CAST(sum(t2.amount) as real)/cast(t1.target as real) * 100) as progres '
               'FROM crapp_projects as t1 left join crapp_donationfund as t2 on t1.id = t2.project_id '
               'group by t1.id, t1.title, t1.details, t1.target, t1.start_date, t1.end_date, t1.creation_date, '
               't1.is_featured, t1.category_id,t1.owner_id')
    #print(sqlquery)
    result = Projects.objects.raw(sqlquery)    
    return result

def projectsprogressbycat(cat):
    sqlquery = ('SELECT t1.id, t1.title, t1.details, t1.target, t1.start_date, t1.end_date, t1.creation_date, '
               't1.is_featured, t1.category_id,t1.owner_id , round(CAST(sum(t2.amount) as real)/cast(t1.target as real) * 100) as progres '
               'FROM crapp_projects as t1 left join crapp_donationfund as t2 on t1.id = t2.project_id '
               'where t1.category_id='+ str(cat) + ' '
               'group by t1.id, t1.title, t1.details, t1.target, t1.start_date, t1.end_date, t1.creation_date, '
               't1.is_featured, t1.category_id,t1.owner_id')
    #print(sqlquery)
    result = Projects.objects.raw(sqlquery)    
    return result

def projectsprogressbyuser(user):
    sqlquery = ('SELECT t1.id, t1.title, t1.details, t1.target, t1.start_date, t1.end_date, t1.creation_date, '
               't1.is_featured, t1.category_id,t1.owner_id , round(CAST(sum(t2.amount) as real)/cast(t1.target as real) * 100) as progres '
               'FROM crapp_projects as t1 left join crapp_donationfund as t2 on t1.id = t2.project_id '
               'where t1.owner_id='+ str(user) + ' '
               'group by t1.id, t1.title, t1.details, t1.target, t1.start_date, t1.end_date, t1.creation_date, '
               't1.is_featured, t1.category_id,t1.owner_id')
    #print(sqlquery)
    result = Projects.objects.raw(sqlquery)    
    return result


def EditProject(request, id):    
    myuser = get_object_or_404(Profile, user_id=request.user.id) 
    projectc = get_object_or_404(Projects, id=id)
    projectform = ProjectFormExtend(instance=projectc)
    if request.method == "GET":     
        context = {"projectform":projectform, "myuser":myuser, "projectc": projectc }
        return render(request, "crapp/editproject.html", context)
    elif request.method == "POST":
        print("Hello")
        form = ProjectFormExtend(request.POST, request.FILES,  instance=projectc)   
        files = request.FILES.getlist('images')
        if form.is_valid():
            new = form.save(commit=False)               
            new.save()
            form.save_m2m()
            if files:
                for f in files:
                    ProjectPictures.objects.create(project_id=new, picture_label=form.cleaned_data.get('title'), picture=f)
                    
            return redirect('projectdetails', id)
        else:
            #form =CustomUserCreationForm()
            print("Not Valid")
            print(form.errors)
            context = {"projectc":projectc, "myuser":myuser , "projectc": projectc}
            return render(request, "crapp/editproject.html", context)

def CancelProject(request, id):
    project = get_object_or_404(Projects, id=id)
    donations = DonationFund.objects.filter(project=id).all().aggregate(Sum('amount'))['amount__sum']
    if donations is None:
        donations = 0
    if donations/project.target < 0.25:
        project.delete()
    return redirect('home')

def search(request, search):
     if request.method == "GET":
        myuser = get_object_or_404(Profile, user_id=request.user.id) 
        titlematch = Projects.objects.filter(title__icontains=search)[:5]
        tagsmatch = Projects.objects.filter(tags__name__icontains=search)[:5]
        context = {'now': datetime.datetime.now(),"myuser":myuser, "searchtxt":search, "titlematch": titlematch, "tagsmatch":tagsmatch}
        return render(request, "crapp/searchresult.html", context)
     if request.method == "POST":
        search = request.POST.get('searchtext')
        return redirect('search', search)
    