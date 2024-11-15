from django.db import models

from account.models import User

# Create your models here.

class Team(models.Model):
    image = models.ImageField(upload_to='team_images')
    full_name = models.CharField(max_length=99)
    role = models.CharField(max_length=99)
    bio = models.TextField(max_length=199)
    twitter_link = models.URLField(blank=True, null=True)
    facebook_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)

class Contact(models.Model):
    address = models.CharField(max_length=99)
    phone = models.CharField(max_length=19)
    email = models.EmailField(max_length=99)
    twitter_link = models.URLField(blank=True, null=True)
    facebook_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)

class Category(models.Model):
    name = models.CharField(max_length=19, unique=True)
    
    def __str__(self):
        return self.name

class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    action = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
