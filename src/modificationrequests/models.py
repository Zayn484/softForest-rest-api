from django.contrib.auth import settings
from django.db import models
from django.db.models.signals import post_save
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import FileSystemStorage

# Create your models here.

User = settings.AUTH_USER_MODEL


def upload_file_loc(instance, filename):
    location = "attachment/{}/".format(instance.request.id)
    return location + filename


class RequestManager(models.Manager):
    def all(self):
        qs = super(RequestManager, self).all()
        return qs

    def create_by_model_type(self, model_type, slug, developer_id, content, days, budget, user):
        model_qs = ContentType.objects.filter(model=model_type)
        if model_qs.exists():
            SomeModel = model_qs.first().model_class()
            obj_qs = SomeModel.objects.filter(slug=slug)
            if obj_qs.exists() and obj_qs.count() == 1:
                instance = self.model()
                instance.content = content
                instance.days = days
                instance.budget = budget
                instance.user = user.first()
                instance.content_type = model_qs.first()
                instance.object_id = obj_qs.first().id
                instance.developer_id = developer_id
                instance.save()
                return instance
        return None


class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    developer_id = models.PositiveIntegerField()
    content = models.TextField()
    days = models.PositiveIntegerField()
    budget = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    status = models.CharField(max_length=50, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    objects = RequestManager()

    def __str__(self):
        return str(self.user)


class File(models.Model):
    request = models.ForeignKey(Request, related_name='file', on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_file_loc, storage=FileSystemStorage(location=settings.PROTECTED_ROOT))

    def __str__(self):
        return str(self.file.name)

    @property
    def name(self):
        return self.file.name


def request_post_reciever(sender, instance, created, **kwargs):
    status = instance.status
    if status == 'declined':
        qs = Request.objects.filter(id=instance.id).update(developer_id=0)
        return qs


post_save.connect(request_post_reciever, sender=Request)
