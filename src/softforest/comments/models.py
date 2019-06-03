from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.db import models
from projects.models import Project
import statistics


class CommentManager(models.Manager):
    def all(self):
        qs = super(CommentManager, self).filter(parent=None)
        return qs

    def filter_by_instance(self, instance):
        content_type = ContentType.objects.get_for_model(instance.__class__)
        obj_id = instance.id
        qs = super(CommentManager, self).filter(content_type=content_type, object_id=obj_id).filter(parent=None)
        return qs

    def create_by_model_type(self, model_type, slug, content, rating, user, parent_obj=None):
        model_qs = ContentType.objects.filter(model=model_type)
        if model_qs.exists():
            SomeModel = model_qs.first().model_class()
            obj_qs = SomeModel.objects.filter(slug=slug)
            if obj_qs.exists() and obj_qs.count() == 1:
                instance = self.model()
                instance.content = content
                instance.rating = rating
                instance.user = user.first()
                instance.content_type = model_qs.first()
                instance.object_id = obj_qs.first().id
                if parent_obj:
                    instance.parent = parent_obj
                instance.save()
                update_project_rating(obj_qs)
                return instance
        return None


class Comment(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)

    content = models.TextField()
    rating = models.DecimalField(default=0.0, max_digits=2, decimal_places=1, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = CommentManager()

    class Meta:
        ordering = ['-timestamp']

    def __unicode__(self):
        return str(self.user)

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse("comments:thread", kwargs={"id": self.id})

    def get_delete_url(self):
        return reverse("comments:delete", kwargs={"id": self.id})

    def children(self):  # replies
        return Comment.objects.filter(parent=self)

    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True


def update_project_rating(instance):

    slug = instance.first().slug
    object_id = instance.first().id
    comment_ratings = Comment.objects.filter(object_id=object_id).values('rating')
    rating_list = [obj.get("rating") for obj in comment_ratings]
    mean = statistics.mean(rating_list)
    round_mean = round(mean, 1)
    qs = Project.objects.filter(slug=slug).update(ratings=round_mean)
