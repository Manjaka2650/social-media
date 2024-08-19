from django.contrib import admin

# Register your models here.
from .models import CustomUser,Commentaire,Posts,Amis,Like,Request,Follow,SavedPost
admin.site.register(Commentaire)
admin.site.register(CustomUser)
admin.site.register(Posts)
# admin.site.register(Amis)
admin.site.register(Like)
admin.site.register(SavedPost)
admin.site.register(Follow)
