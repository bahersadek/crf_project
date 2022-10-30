from django.db import models
from django.contrib.auth.models import User, BaseUserManager, AbstractBaseUser
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


PHONE_REGEX = RegexValidator(
    r'^01[0-2][0-9]{8}$', 'Egyptian phone number is required')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, validators=[PHONE_REGEX],  verbose_name='phone')
    image = models.ImageField(upload_to='profile_pics')
    signup_confirmation = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

