from django.db import models

# Create your models here.

class UserResponse(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    response = models.JSONField()
