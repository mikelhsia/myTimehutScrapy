from django.db import models
from django.conf import settings

from django.urls import reverse

from django.utils.text import slugify
import django.db.models.deletion

# Create your models here.
class Image(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='images_created',
	                         on_delete=django.db.models.deletion.DO_NOTHING)   # User who added this
	title = models.CharField(max_length=200)                                   # title of images
	slug = models.CharField(max_length=200, blank=True)                        # short label, SEO friendly url
	url = models.URLField()                                                    # original URL
	image = models.ImageField(upload_to='images/%Y/%m/%d')                     # image file
	description = models.TextField(blank=True)                                 # optional description of image

	# db_index = True, and Django creates index in DB for this field
	# Consider setting db_index=True for fields that you frequently query using filter(), exclude(), or order_by().
	# ForeignKey fields or fields with unique=True imply the creation of an index. You can also use Meta.index_together
	# to create indexes for multiple fields.
	created = models.DateField(auto_now_add=True, db_index=True)               # created at flag

	# When you define a ManyToManyField, Django creates an intermediary join table using the primary
	# keys of both models. The ManyToManyField can be defined in any of the two related models.
	users_like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='images_liked', blank=True)

	total_likes = models.PositiveIntegerField(db_index=True, default=0)

	def get_absolute_url(self):
		return reverse('images:detail', args=[self.id, self.slug])

	def __str__(self):
		return self.title

	def save(self, *args, **kwargs):
		if not self.slug:
			# slugify to automatically generate the image slug for the given title when no slug is provided
			self.slug = slugify(self.title)
			super(Image, self).save(*args, **kwargs)