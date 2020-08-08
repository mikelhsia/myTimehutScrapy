from django import forms
from .models import Image

# Lib for overriding the save() method of a ModelForm
from urllib import request
from django.core.files.base import ContentFile
from django.utils.text import slugify

class ImageCreateForm(forms.ModelForm):

	def clean_url(self):
		url = self.cleaned_data['url']
		valid_extensions = ['jpg', 'jpeg']
		extension = url.rsplit('.', 1)[1].lower()

		if extension not in valid_extensions:
			raise forms.ValidationError('The given URL does not match valid image extensions.')

		return url

	# Overriding the save() method to retrieve the given image and save it
	def save(self, force_insert=False, force_update=False, commit=True):
		image = super(ImageCreateForm, self).save(commit=False)
		image_url = self.cleaned_data['url']
		image_name = f'{slugify(image.title)}.{image_url.rsplit(".", 1)[1].lower()}'

		# download image from the given URL
		response = request.urlopen(image_url)

		# image field passing it a ContentFile object that is instantiated with the downloaded file contents.
		# In this way we save the file to the media directory of our project.
		# save=False to avoid saving the object to database yet.
		image.image.save(image_name, ContentFile(response.read()), save=False)

		if commit:
			image.save()

		return image

	class Meta:
		model = Image
		fields = ('title', 'url', 'description')
		# Making url hidden it's because the user is not going to input the url manually
		# url will come from external website
		widgets = {
			'url': forms.HiddenInput,
		}