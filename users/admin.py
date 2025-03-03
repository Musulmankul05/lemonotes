from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    fields = ('username', ('first_name', 'last_name',), 'email',)
    list_display = ['username', 'first_name', 'last_name', 'email']
