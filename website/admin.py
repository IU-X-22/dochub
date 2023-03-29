from django.contrib import admin
from website.models import *
from django.contrib.auth.admin import UserAdmin

admin.site.register(Document)
admin.site.register(GroupDocuments)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

