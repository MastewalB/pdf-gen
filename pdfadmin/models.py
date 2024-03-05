import uuid
from django.db import models

# Create your models here.

class QuestionSection(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable=False, unique = True)
    title = models.TextField()

class Question(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable=False, unique = True)
    section = models.ForeignKey(QuestionSection, on_delete=models.CASCADE)
    content = models.TextField()
    correctAnswer = models.CharField(max_length=250)
    suggestion = models.TextField()
