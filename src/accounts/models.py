from django.db import models
from django.db.models.signals import post_save,pre_save
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings
import random
import os
import string
from chat.models import Contact
from datetime import datetime,timedelta
from random import randint
from django.core.mail import EmailMessage

# Create your models here.


def create_unique_id():
    return ''.join(random.choices(string.digits, k=8))


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    new_filename = random.randint(1, 3243245123)
    name, ext = get_filename_ext(filename)
    final_filename = f'{new_filename}{ext}'
    return f'profile/{new_filename}/{final_filename}'


class UserManager(BaseUserManager):
    """Helps Django works with our custom user model"""

    def create_user(self, email, username, password=None, occupation=None):
        """Create new user profile object"""

        if not email:
            raise ValueError('Email is empty')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, occupation=occupation)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, username, password):
        """This will create and save new super user with given details"""

        user = self.create_user(email, username, password)
        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Represents user profile in our system"""

    id = models.IntegerField(primary_key=True, default=create_unique_id)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    occupation = models.CharField(max_length=120, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_full_name(self):
        """Used to get user's full name"""

        return self.username

    def get_short_name(self):
        """Used to get user's short name"""

        return self.username

    def __str__(self):
        """Django uses object to convert the object to a string"""
        return self.email


class Profile(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             related_name='profile', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    profile_name = models.CharField(max_length=120, blank=True, null=True)
    profile_title = models.CharField(max_length=250, blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    skills = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return str(self.user)


class Recommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='recommendations',
                             on_delete=models.CASCADE)
    categories = models.TextField(blank=True, null=True)
    technologies = models.TextField(blank=True, null=True)
    knowledge = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)


# Creating contact from chat
def user_post_reciever(sender, instance, created, **kwargs):
    if created:
        Contact.objects.create(user=instance)


post_save.connect(user_post_reciever, sender=User)

def random_code_generator():
    range_start = 10 ** (6 - 1)
    range_end = (10 ** 6) - 1
    return randint(range_start, range_end)

class ForgetPassword(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    code = models.CharField(null=True,blank=True,max_length=6)
    timestamp = models.DateTimeField(default=datetime.now()+timedelta(minutes=60))

    def __str__(self):
        return str(self.user)

def forgetPassword_pre_save(sender, instance, *args, **kwargs):
    instance.code = str(random_code_generator())
    if instance.code:
        try:
            message = f'Your account verification Code for Forget Password is {instance.code}\nThanks For using SoftForest\nThe SoftForest Team'
            email = EmailMessage(
                f'Hi {instance.user.email} ',
                message,
                settings.EMAIL_HOST_USER,
                [instance.user.email],
                headers={'Message-ID': f'{instance.code}'},
            )
            email.send(fail_silently=True)
            print(email)

        except Exception as e:
            print(e)


pre_save.connect(forgetPassword_pre_save,sender=ForgetPassword)

