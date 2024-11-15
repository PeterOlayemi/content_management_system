from django.db import models

from account.models import User
from writer.models import Article

# Create your models here.

class Comment(models.Model):
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='replies')
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.writer} comments - '{self.content}'"
    
    @property
    def children(self):
        return Comment.objects.filter(parent=self).reverse()

    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False
    