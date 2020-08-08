from django.contrib.auth.models import User

class EmailAuthBackend(object):
	'''
	Authenticate using e-mail account
	'''
	def authenticate(self, username=None, password=None):
		'''
		We try to retrieve a user with the given e-mail address and check the password using the
		built-in check_password() method of the User model. This method handles the password hashing
		to compare the given password against the password stored in the database.
		:param username:
		:param password:
		:return:
		'''
		try:
			user = User.objects.get(email=username)

			if user.check_password(password):
				return user
			return None
		except User.DoesNotExist:
			return None

	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None