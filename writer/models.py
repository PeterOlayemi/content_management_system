from django.db import models

from account.models import User
from administrator.models import Category

# Create your models here.

class Article(models.Model):

    STATUS = (
        ('DRAFT', 'DRAFT'),
        ('PUBLISH', 'PUBLISH'),
    )

    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ManyToManyField(Category, related_name='article_category')
    title = models.CharField(max_length=99, unique=True)
    content = models.TextField()
    image = models.ImageField(upload_to='article_images')
    status = models.CharField(max_length=19, choices=STATUS, default='DRAFT')
    likes = models.ManyToManyField(User, related_name='article_like', blank=True)
    views = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"'{self.title}' by {self.writer.username}"
    
    def number_of_likes(self):
        return self.likes.count()
