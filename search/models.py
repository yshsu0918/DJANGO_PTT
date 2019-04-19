from django.db import models

# Create your models here.
class Ptt(models.Model):
    hash = models.CharField(max_length=100,primary_key=True)
    ID = models.CharField(max_length=100)
    content = models.CharField(max_length=100000)
    time = models.CharField(max_length=100)
    link = models.CharField(max_length=100)

class Querywho(models.Model):
    id = models.CharField(max_length=100,primary_key=True)
