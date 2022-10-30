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
    #projectc = get_object_or_404(Projects, p_id=id)
    project = Projects.objects.filter(id=id).all()    
    images = ProjectPictures.objects.filter(project_id=id).all()    
    donations = DonationFund.objects.filter(project=id).all()
    tags = Projects.tags.all()
    
    #totalrate = Projects.objects.filter(ratings__isnull=False).only('ratings__average')
    #totalrate = Projects.objects.select_related('ratings').filter(id=id)
    #print(totalrate)
    donatorcount = DonationFund.objects.filter(project=id).all().annotate(count=Count('donator'))
    totalfund = DonationFund.objects.filter(project=id).all().aggregate(Sum('amount'))['amount__sum']
    
    context = {"project":project, "images":images, "donations": donations, "tags": tags, "donatorcount": donatorcount, "totalfund": totalfund}
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
    pass