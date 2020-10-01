from django.db import models

# Create your models here.
class ReadBooks(models.Model):
    username = models.CharField(max_length=200)
    read = models.CharField(max_length=500)