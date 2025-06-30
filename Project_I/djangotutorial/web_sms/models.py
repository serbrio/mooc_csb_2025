from django.db import models

from django.contrib.auth.models import User

from django.utils import timezone


# Create your models here.

class Account(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	balance = models.IntegerField()
	

class Message(models.Model):
	text = models.CharField(max_length=200)
	sender = models.ForeignKey(Account, null=True, related_name="sender", on_delete=models.CASCADE)
	receiver = models.ForeignKey(Account, null=True, related_name="receiver", on_delete=models.CASCADE)
	date = models.DateTimeField("date sent", default=timezone.now)