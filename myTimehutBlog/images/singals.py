from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Image

# First we register the users_like_changed function as a receiver function using "receiver()" decorator
# And attach it to the m2m_changed signal
# We connect the function to Image.users_like.through so that the function is only called if the
# m2m_changed signal has been launched by this sender.
@receiver(m2m_changed, sender=Image.users_like.through)
def users_like_change(sender, instance, **kwargs):
	instance.total_likes = instance.users_like.count()
	instance.save()