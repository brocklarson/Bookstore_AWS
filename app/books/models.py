from django.db import models

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=250, blank=False, default='')
    price = models.FloatField(blank=False, default=0.0)
    paperback = models.BooleanField(blank=False, default=True)
    available = models.CharField(max_length=15, blank=False, default=True)
    authors = models.ManyToManyField('Author', blank=False, related_name='books')

    def __str__(self):
        return self.title
    

class Author(models.Model):
    name = models.CharField(max_length=100, blank=False, default='')

    def __str__(self):
        return self.name
    
