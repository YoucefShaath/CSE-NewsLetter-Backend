from django.contrib import admin
from .models import User, Post, Comment, LikedPost, SavedPost, DepartmentSubscription

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(LikedPost)
admin.site.register(SavedPost)
admin.site.register(DepartmentSubscription)

