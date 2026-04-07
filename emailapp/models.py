from django.db import models
from django.contrib.auth.models import User

class EmailLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    to = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)


class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()