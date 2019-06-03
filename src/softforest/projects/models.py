from django.contrib.contenttypes.models import ContentType
from django.db import models
from django_random_queryset import RandomManager
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import pre_save
from softforest.utils import unique_slug_generator
import random
import os

# Create your models here.

user = settings.AUTH_USER_MODEL


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    ctype = ContentType.objects.get_for_model(instance)
    new_filename = random.randint(1, 3243245123)
    name, ext = get_filename_ext(filename)
    final_filename = f'{new_filename}{ext}'
    if str(ctype) == 'project':
        return f'thumbnails/{new_filename}/{final_filename}'
    if str(ctype) == 'snapshot':
        return f'snapshots/{new_filename}/{final_filename}'


def upload_video_path(instance, filename):
    new_filename = random.randint(1, 3243245123)
    name, ext = get_filename_ext(filename)
    final_filename = f'{new_filename}{ext}'
    return f'videos/{new_filename}/{final_filename}'


def upload_project_file_loc(instance, filename):
    slug = instance.project.slug
    if not slug:
        slug = unique_slug_generator(instance.project)
    location = "files/{}/".format(slug)
    return location + filename


class Project(models.Model):
    user = models.ForeignKey(user, null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(blank=True, unique=True)
    image = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    video = models.FileField(upload_to=upload_video_path, null=True, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=120, null=True)
    price = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    service_fees = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    discount_rate = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    ratings = models.DecimalField(default=0.0, max_digits=2, decimal_places=1, null=True, blank=True)
    link = models.CharField(max_length=250, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    on_sale = models.BooleanField(default=False)

    objects = RandomManager()

    def __str__(self):
        return self.title

    def get_downloads(self):
        qs = self.projectfile_set.all()
        return qs


class Snapshot(models.Model):
    project = models.ForeignKey(Project, related_name='snapshots', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_image_path, null=True, blank=True)

    def __str__(self):
        return str(self.project)


class Module(models.Model):
    project = models.ForeignKey(Project, related_name='modules', on_delete=models.CASCADE)
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class Technology(models.Model):
    project = models.ForeignKey(Project, related_name='technologies', on_delete=models.CASCADE)
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class Requirement(models.Model):
    project = models.ForeignKey(Project, related_name='requirements', on_delete=models.CASCADE)
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class ProjectFile(models.Model):
    project = models.ForeignKey(Project, related_name='file', on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_project_file_loc, storage=FileSystemStorage(location=settings.PROTECTED_ROOT))

    def __str__(self):
        return str(self.file.name)

    def get_download_url(self):
        return self.file.url

    @property
    def name(self):
        return self.file.name


def project_pre_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)
        if Project.objects.filter(on_sale=True).count() != 0: # Checking if sale is on
            discount = 30
            multiplier = discount / 100
            old_price = float(instance.price)
            new_price = old_price - (old_price * multiplier)
            instance.discount_rate = round(new_price, 2)
            instance.on_sale = True


pre_save.connect(project_pre_receiver, sender=Project)
