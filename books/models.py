from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Book(models.Model):
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=100, blank=True, default="")
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    publish_date = models.DateField()
    image = models.ImageField(upload_to='media/books')
    genre_choice = [("ro", "romance"), ("hr", 'horror'), ("sc", "science"), ("sf", "science fiction")]
    genre = models.CharField(max_length=2, choices=genre_choice)
    loan = models.ManyToManyField(User, blank=True, null=True)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    number_of_stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True)

    def __str__(self):
        return self.name
