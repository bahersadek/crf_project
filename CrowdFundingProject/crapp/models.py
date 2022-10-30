from django.db import models
from users.models import User
from datetime import timedelta
from taggit.managers import TaggableManager
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
#from djangoratings.fields import RatingField
from star_ratings.models import Rating
from comment.models import Comment
import datetime
from django.urls import reverse

# Create your models here.
class Category(models.Model):
    c_id = models.AutoField(primary_key=True)
    c_name = models.CharField(max_length=200)

    def __str__(self):
        return self.c_name


def get_next_30_days_date():
    return datetime.datetime.now() + timedelta(days=30)

class Projects(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    details = models.TextField(max_length=2000)
    target = models.PositiveIntegerField()

    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    start_date = models.DateTimeField(default=datetime.datetime.now)
    end_date = models.DateTimeField(default=get_next_30_days_date)
    creation_date = models.DateTimeField(default=datetime.datetime.now)
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name="Projects")
    is_featured = models.BooleanField(default=False)
    tags = TaggableManager(blank=True)
    comments = GenericRelation(Comment)
    rating = GenericRelation(Rating, related_query_name='Projects')

    def __str__(self):
        return str(self.title)

    errors = {}

    def clean(self):
        if (self.is_featured == True and Projects.objects.filter(is_featured=True).exclude(id=self.p_id).count() >= 5):
            raise ValidationError(
                {'is_featured': _('You already have five featured campaigns.')})

        valid = True
        start_date = self.start_date
        end_date = self.end_date
        self.errors = {}
        if str(start_date) < str(datetime.date.today()):
            self.errors['date'] = 'invalid date'
            valid = False
        elif str(end_date) == str(start_date):
            self.errors['date'] = 'invalid date'
            valid = False
        elif str(end_date) < str(start_date):
            self.errors['date'] = 'invalid date'
            valid = False
        elif str(end_date) == str(datetime.date.today()):
            self.errors['date'] = 'invalid date'
            valid = False
        if self.title == '':
            self.errors['title'] = 'title is required'
            valid = False
        if self.details == '':
            self.errors['details'] = 'details is required'
            valid = False
        if self.target == '':
            self.errors['target'] = 'target is required'
            valid = False
        return valid

class ProjectPictures(models.Model):
    picture_id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(Projects, on_delete=models.CASCADE)
    picture_label = models.CharField(max_length=50)
    picture = models.ImageField(upload_to='project_pics')

    def __str__(self):
        return self.picture_label

class ProjectReports(models.Model):
    r_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    report = models.TextField(max_length=2000)

    def __str__(self):
        return str(self.report)

def get_set_anon_user():
    return User.objects.get_or_create(first_name='Anonymous', last_name='user')[0]

class DonationFund(models.Model):
    d_id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    donator = models.ForeignKey(User, on_delete=models.SET(get_set_anon_user), default=None)  # type: ignore
    amount = models.PositiveIntegerField()

    def __str__(self):
        return str(self.amount)


