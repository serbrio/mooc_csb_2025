from django.db import models

from django.contrib.auth.models import User

from django.utils import timezone


class Account(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	balance = models.IntegerField()
	secret_question = models.CharField(max_length=100)
	secret_answer = models.CharField(max_length=30)
	## Fix Flaw 2
	"""
	@property
	def password_validator_target(self):
		return self.user.username
	"""
	## End Fix Flaw 2
	

class Message(models.Model):
	text = models.CharField(max_length=200)
	sender = models.ForeignKey(Account, null=True, related_name="sender", on_delete=models.CASCADE)
	receiver = models.ForeignKey(Account, null=True, related_name="receiver", on_delete=models.CASCADE)
	date = models.DateTimeField("date sent", default=timezone.now)