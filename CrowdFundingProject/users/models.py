from django.db import models
from django.contrib.auth.models import User, BaseUserManager, AbstractBaseUser
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date

PHONE_REGEX = RegexValidator(
    r'^01[0-2][0-9]{8}$', 'Egyptian phone number is required')

class Profile(models.Model):
    Country_Choices = (
        ('EG', 'Egypt'),
        ('UAE', 'United Arab Emirates'),
        ('UK', 'United Kingdom'),
        ('USA', 'United States America'),
        ('CA', 'Canda'),
        ('SA', 'Saudi Arabia'),
        ('KW', 'Kuweit'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, validators=[PHONE_REGEX],  verbose_name='phone')
    image = models.ImageField(upload_to='profile_pics')
    signup_confirmation = models.BooleanField(default=False)
    birthdate = models.DateField(default=date.today, blank=True)
    facebook_url = models.CharField(max_length=200, blank=True)
    country = models.CharField(
                        max_length = 50,
                        choices = Country_Choices,
                        blank=True
                        )

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

