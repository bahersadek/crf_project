from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, help_text='Last Name')
    last_name = forms.CharField(max_length=100, help_text='Last Name')
    #email = forms.EmailField(label = "Email")
    phone = forms.CharField()
    image = forms.ImageField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2',)
        enctype="multipart/form-data"

    def save(self, commit=True): 
        obj = super().save(commit=False)
        # do you logic here for example:
        obj.email = self.cleaned_data["username"]
        
        if commit:
            # Saving your obj
            obj.save()
        return obj
# class CustomUserCreationForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = "__all__"