from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from s3direct.fields import S3DirectField


class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    usn= models.CharField(max_length=15, null=True, blank=True, unique=True)

    # def __str__(self):
    #     return self.usn


class Img(models.Model):
    img = models.ImageField(null=False, upload_to='face_img/')



