from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    
    ROLE = [
        ('Reader', 'Reader'),
        ('Writer', 'Writer')
    ]
    
    email = models.EmailField(max_length=99, unique=True)
    role = models.CharField(max_length=10, choices=ROLE)
    
    # writer
    full_name = models.CharField(max_length=19, blank=True, null=True)
    bio = models.TextField(max_length=499, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    website_link = models.URLField(blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)
    facebook_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)
