from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.search import  SearchVectorField 


class GroupDocuments(models.Model):
    name = models.TextField(unique=True)
    uuid_name = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False,
        db_index=True)
    datetime = models.DateTimeField()
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_uuid(self):
        return self.uuid_name


def content_file_name(instance, filename):
    return '/'.join(['documents', str(instance.group_uuid.name), filename])


class Document(models.Model):
    document = models.FileField(null=False, upload_to=content_file_name)
    uuid_name = models.UUIDField(
        primary_key=True, unique=True, default=uuid.uuid4, editable=False,
        db_index=True)
    name = models.TextField()
    description = models.TextField()
    text = models.TextField()
    read_status = models.IntegerField(default=0)
    ''' 
    0 - обрабатывается
    1 - Ожидает проверки
    2 - готов

    '''
    datetime = models.DateTimeField()
    group_uuid = models.ForeignKey(
        'GroupDocuments', on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    def get_url(self):
        return self.document.url


class CustomUser(AbstractUser):
    position = models.TextField()

class QueueStatus(models.Model):
    max_progress = models.IntegerField(default=0)
    actual_progress = models.IntegerField(default=0)
