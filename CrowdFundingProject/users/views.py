from django.contrib.auth import login
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from users.forms import CustomUserCreationForm, UserProfileForm
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.contrib.auth.models import User
from crapp.models import *
from .models import Profile
from django.db.models import Count, Sum

# Create your views here.
def dashboard(request):
    return render(request, "users/dashboard.html")

def activation_sent_view(request):
    return render(request, 'registration/activation_sent.html')

def activate(request, uidb64, token, backend='django.contrib.auth.backends.ModelBackend'):
    try:
        #print(uidb64)
        uid = force_str(urlsafe_base64_decode(uidb64))
        #print(uid)
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        # if valid set active true 
        user.is_active = True
        # set signup_confirmation true
        user.profile.signup_confirmation = True
        user.save()
        login(request, user,backend='django.contrib.auth.backends.ModelBackend')
        return render(request, "users/dashboard.html")
    else:
        return render(request, 'registration/activation_invalid.html')

def register(request):
    if request.method == "GET":
        return render(
            request, "users/register.html",
            {"form": CustomUserCreationForm}
        )
    elif request.method == "POST":
        print("Hello")
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            print(form.cleaned_data.get("image"))
            user = form.save()
            user.refresh_from_db()
            user.profile.first_name = form.cleaned_data.get('first_name')
            user.profile.last_name = form.cleaned_data.get('last_name')
            user.profile.phone = form.cleaned_data.get('phone')
            user.profile.image = form.cleaned_data.get("image")
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            message = render_to_string('users/activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # method will generate a hash value with user related data
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('activation_sent')
        else:
            #form =CustomUserCreationForm()
            print("Not Valid")
            print(form.errors)
            return render(request, 'users/register.html', {'form': form})

@login_required
def UserProfile(request):
    #userporfile = Profile.objects.filter(user=request.user).all()
    myuser = get_object_or_404(Profile, user_id=request.user.id) 
    projects = Projects.objects.filter(owner=request.user).all()
    print(len(projects))
    donation = DonationFund.objects.filter(donator=request.user).all()
    print(len(donation))
    totalfund = DonationFund.objects.filter(donator=request.user).all().aggregate(Sum('amount'))['amount__sum']
    context = {"donation":donation,"projects":projects, 
                "myuser":myuser,"totalfund":totalfund,
                "projectcount":len(projects), "donationcount":len(donation) }
    return render(request, "users/userprofile.html", context)

@login_required  
def EditUserProfile(request):    
    myuser = get_object_or_404(Profile, user_id=request.user.id) 
    userprofile = UserProfileForm(instance=myuser)
    instance_user = User.objects.get(pk=request.user.id)
    if request.method == "GET":        
        context = {"userprofile":userprofile, "myuser":myuser }
        return render(request, "users/editprofile.html", context)
    elif request.method == "POST":
        print("Hello")
        form = UserProfileForm(request.POST, request.FILES,  instance=myuser)
        if form.is_valid():            
            user = form.save()
            user.refresh_from_db()
            print(instance_user.first_name)
            print(form.cleaned_data.get('first_name'))
            instance_user.first_name = form.cleaned_data.get('first_name')
            instance_user.last_name = form.cleaned_data.get('last_name')
            instance_user.save()
            return redirect('userprofile')
        else:
            #form =CustomUserCreationForm()
            print("Not Valid")
            print(form.errors)
            return render(request, 'users/editprofile.html', {'userprofile': form})

def deleteaccount(request):
    myuser = get_object_or_404(Profile, user_id=request.user.id) 
    userprofile = UserProfileForm(instance=myuser)
    print("hello")
    if request.method == "GET":        
        context = {"userprofile":userprofile, "myuser":myuser, "error":"" }
        return render(request, "users/deleteaccount.html", context)
    elif request.method == "POST":
        print("test")
        password = request.POST.get("passwordinput")
        username = request.POST.get("usernameinput")
        is_password_correct = request.user.check_password(password)
        if username==request.user.username and is_password_correct:            
            request.user.delete()
            return redirect('logout')
        else:   
            context = {"userprofile":userprofile, "myuser":myuser, "error":"Invalid Credentials" }        
            return render(request, 'users/deleteaccount.html', context)

