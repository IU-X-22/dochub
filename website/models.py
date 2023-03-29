from django.db import models
import uuid
from django.db.models import Model
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField


from mindmap import settings

class GroupDocuments(models.Model):
    name = models.TextField(unique=True)
    uuid_name = models.UUIDField(primary_key = True,unique=True,default = uuid.uuid4,editable = False)
    datetime = models.DateTimeField()
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    def get_uuid(self):
        return self.uuid_name

def content_file_name(instance, filename):
    print(instance)
    return '/'.join(['documents', str(instance.group_folder.name), filename])

class Document(models.Model):
    document = models.FileField(null=False, upload_to=content_file_name)
    uuid_name = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    description = models.TextField()
    text = models.TextField()

   # text = ArrayField(models.CharField(max_length=100), blank=False)
    datetime = models.DateTimeField()
    group_folder =  models.ForeignKey('GroupDocuments', on_delete=models.PROTECT) # Many-to-Many
    group_uuid = models.UUIDField(unique=False,default = uuid.uuid4,editable = True)
    #folder = models.ForeignKey('GroupDocuments', on_delete=models.PROTECT)
    def __str__(self):
        return self.name    
        
    def get_url(self):
        return self.document.url


class CustomUser(AbstractUser):
    position = models.TextField() 

