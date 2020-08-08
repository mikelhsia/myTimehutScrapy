from django.apps import AppConfig


class ImagesConfig(AppConfig):
	# The name attribute defines the full Python path to the application.
	# The verbose_name attribute sets the human - readable name for this application. It's displayed in the administration site.
	name = 'images'
	verbose_name = 'Image bookmarks'

	# The ready() method is where we import the signals for this application
	def ready(self):
		# import signal handlers
		# import images.signals
		pass
