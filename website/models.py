from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser


class GroupDocuments(models.Model):
    name = models.TextField(unique=True)
    uuid_name = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    datetime = models.DateTimeField()
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_uuid(self):
        return self.uuid_name

def content_file_name(instance, filename):
    return '/'.join(['documents', str(instance.group_folder.name), filename])


class Document(models.Model):
    document = models.FileField(null=False, upload_to=content_file_name)
    uuid_name = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    description = models.TextField()
    text = models.TextField()
    is_readed = models.BooleanField(default=False)
    datetime = models.DateTimeField()
    group_folder = models.ForeignKey(
        'GroupDocuments', on_delete=models.PROTECT)
    group_uuid = models.UUIDField(
        unique=False, default=uuid.uuid4, editable=True)

    def __str__(self):
        return self.name

    def get_url(self):
        return self.document.url


class CustomUser(AbstractUser):
    position = models.TextField()



class Quote(models.Model):
    name = models.CharField(max_length=250)
    quote = models.TextField(max_length=1000)

    def __str__(self):
        return self.quote