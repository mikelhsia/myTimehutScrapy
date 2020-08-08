import datetime
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import Action

def create_action(user, verb, target=None):
	# Check for any similar action made in the last minute
	now = timezone.now()
	# We use the last_minute variable to store the datime one minute ago and we retrieve any identical actions performed by the user since then
	last_minute = now - datetime.timedelta(seconds=60)
	similar_actions = Action.objects.filter(user_id=user.id, verb=verb, created__gte=last_minute)

	if target:
		target_ct = ContentType.objects.get_for_model(target)
		similar_actions = similar_actions.filter(target_ct=target_ct, target_id=target.id)

	if not similar_actions:
		# We create Action object if no identical actions found
		action = Action(user=user, verb=verb, target=target)
		action.save()

		return True

	return False
