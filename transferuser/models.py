from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class InnAccUser(models.Model):
	account = models.FloatField(default=0.0)
	inn = models.TextField(default='')
	user = models.OneToOneField(User,
		on_delete=models.CASCADE,
		related_name='inn_acc',
		null=True)

def generate_on_create(sender,instance,created,*args,**kwargs):
	if created:
		InnAccUser.objects.create(user=instance)

post_save.connect(generate_on_create,
	sender=User)