from django.contrib import admin

# Register your models here.
from .models import Message,Room,Notification

admin.site.register(Message)
admin.site.register(Room)
admin.site.register(Notification)