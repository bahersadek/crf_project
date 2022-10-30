from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Projects, Category, ProjectPictures

class ProjectForm(forms.ModelForm):

    class Meta:
        model = Projects
        fields = ['title', 'details', 'target','start_date', 'end_date', 'category', 'tags']
    
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['details'].widget.attrs.update({'class': 'form-control'})
        self.fields['target'].widget.attrs.update({'class': 'form-control'})
        self.fields['start_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['end_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['tags'].widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if end_date <= start_date:
            msg = u"End date should be greater than start date."
            self._errors["end_date"] = self.error_class([msg])

class ProjectFormExtend(ProjectForm):
    images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    
    class Meta(ProjectForm.Meta):
        fields = ProjectForm.Meta.fields + ['images',]

class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = "__all__"

class ProjectPictureForm(forms.ModelForm):
    
    class Meta:
        model = ProjectPictures
        fields = ('picture',)