from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse
from users.forms import CustomUserCreationForm
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.contrib.auth.models import User


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