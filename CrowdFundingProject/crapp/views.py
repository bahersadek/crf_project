from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.conf import settings
from django.templatetags.static import static
from django.contrib import messages
from django.forms import modelformset_factory
from taggit.models import Tag

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
    context = {"allprojects": allprojects}
    return render(request, "crapp/projects.html", context)

def ProjectDetails(request,id):
    #projectc = get_object_or_404(Projects, p_id=id)
    project = Projects.objects.filter(id=id).all()
    print(project)
    images = ProjectPictures.objects.filter(project_id=id).all()
    print(images)
    donations = DonationFund.objects.filter(project=id).all()
    tags = Projects.tags.all()
    context = {"project":project, "images":images, "donations": donations, "tags": tags}
    return render(request, "crapp/projectdetails.html", context)
