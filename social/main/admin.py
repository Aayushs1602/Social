from django.contrib import admin
from .models import Profile, Post, likePost, FollwersCount

# Register your models here.
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(likePost)
admin.site.register(FollwersCount)
