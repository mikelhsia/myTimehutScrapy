# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.conf import settings

# we will use the reverse() method that allows you to build URLs by their name and passing optional parameters.
from django.urls import reverse

from django.contrib.auth.models import User

# Create your manager here.
class MomentManager(models.Manager):
	def get_pic_moment(self):
		return super(MomentManager, self).get_queryset().filter(content_type=3)

# Create your models here.
class Contact(models.Model):
	user_from = models.ForeignKey(User, related_name='rel_from_set', on_delete=models.DO_NOTHING)
	user_to = models.ForeignKey(User, related_name='rel_to_set', on_delete=models.DO_NOTHING)
	created = models.DateTimeField(auto_now_add=True, db_index=True)

	class Meta:
		ordering = ('-created',)

	def __str__(self):
		return f"{self.user_from} follows {self.user_to}"

User.add_to_class('following', models.ManyToManyField('self', through=Contact, related_name='followers', symmetrical=False))
'''
We can't alter the User class directly because it belongs to the django.contrib.auth application
We are going to take a slightly different approach, by adding this field dynamically to the user model (Monkey-patch)
- tell Django to use our custom intermediary model for the relationship by adding through=Contact to the ManyToManyField.
------------------------------
Keep in mind that in most cases, it is preferable to add fields to the Profile model we created before, 
instead of monkey-patching the User model. Django also allows you to use custom user models.
------------------------------
Django forces the relationship to be symmetrical. In this case, we are setting symmetrical=False to define a 
non-symmetric relation. This is, if I follow you, it doesn't mean you automatically follow me.
'''

class Profile(models.Model):
	'''
	Extending User model
	'''
	# AUTH_USER_MODEL setting to refer to it when defining model's relations to the user model,
	# instead of referring to the auth User model directly
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
	date_of_birth = models.DateField(blank=True, null=True)
	# You will need to install one of the Python packages to manage images, which are PIL (Python Imaging Library) or Pillow
	photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)

	@property
	def has_profile_image(self):
		if self.photo != "":
			return True
		return False

	@property
	def profile_image_url(self):
		if self.photo and hasattr(self.photo, 'url'):
			return self.photo.url
		return None

	def __str__(self):
		return f'Profile for user {self.user.username}'

class PeekabooCollection(models.Model):

	COLLECTION_TYPE =  (
		(1, 'Collection'),
		(2, 'Text'),
		(3, 'Picture'),
		(4, 'Video'),
	)

	# The convention in Django is to add a get_absolute_url() method to the model that returns the canonical URL of the object.
	def get_absolute_url(self):
		# reverse need to first have url pattern in urls.py named
		return reverse('timehutBlog:collection_detail', args=[self.id])

	# null 是针对数据库而言，如果
	# null = True, 表示数据库的该字段可以为空。
	# blank 是针对表单的
	# blank = True, 表示你的表单填写该字段的时候可以不填
	id = models.CharField(primary_key=True, max_length=32)
	baby_id = models.CharField(max_length=32, blank=True, null=True)
	created_at = models.IntegerField(blank=True, null=True)
	updated_at = models.IntegerField(blank=True, null=True)
	months = models.IntegerField(blank=True, null=True)
	days = models.IntegerField(blank=True, null=True)
	content_type = models.SmallIntegerField(blank=True, null=True)
	caption = models.TextField(blank=True, null=True)
	'''
		# unique_for_date parameter to this field so we can build URLs
		# for posts using the date and slug of the post. Django will prevent from
		# multiple posts having the same slug for the same date
		slug = models.SlugField(max_length=250, unique_for_date='created_at')
	'''

	class Meta:
		# managed = False
		# managed＝True则告诉django可以对数据库进行操作
		managed = True
		db_table = 'peekaboo_collection'
		ordering = ('-created_at',)

	# 修改admin后台的显示
	# def __str__(self):
	# 	return f"{self.baby_id} - {self.id}"


class PeekabooMoment(models.Model):
	MOMENT_TYPE =  (
		(1, 'Text'),
		(2, 'Rich_text'),
		(3, 'Picture'),
		(4, 'Video'),
	)

	id = models.CharField(primary_key=True, max_length=32)
	event = models.ForeignKey(PeekabooCollection, on_delete=models.DO_NOTHING,
	                             related_name='event_id', blank=True, null=True)
	baby_id = models.CharField(max_length=32, blank=True, null=True)
	created_at = models.IntegerField(blank=True, null=True)
	updated_at = models.IntegerField(blank=True, null=True)
	content_type = models.SmallIntegerField(blank=True, null=True)
	content = models.TextField(blank=True, null=True)
	src_url = models.CharField(max_length=512, blank=True, null=True)
	months = models.IntegerField(blank=True, null=True)
	days = models.IntegerField(blank=True, null=True)

	class Meta:
		managed = True
		db_table = 'peekaboo_moment'
		ordering = ('-created_at',)

	# The default manager
	objects = models.Manager()
	# Our custom manager
	# In Shell: Moment.getPictureContent.get_pic_moment()
	getPictureContent = MomentManager()

class PeekabooCollectionComment(models.Model):
	# The related_name attribute allows us to name the attribute that we use for the relation from the related
	# object back to this one. After defining this, we can
	# 1. Retrieve the collection of a comment object using comment.collection and
	# 2. Retrieve all comments of a post using collection.comments.all().
	# If you don't define the related_name attribute, Django will use the undercase name of the model
	# followed by _set (that is, comment_set) to name the manager of the related object back to this one.
	collection = models.ForeignKey(PeekabooCollection, on_delete=models.DO_NOTHING, related_name='comments')
	name = models.CharField(max_length=80)
	email = models.EmailField()
	body = models.TextField()

	# auto_now_add here, the date will be saved automatically when creating an object
	created_at = models.DateTimeField(auto_now_add=True)

	# auto_now here, the date will be updated automatically when saving an object.
	updated_at = models.DateTimeField(auto_now=True)
	active = models.BooleanField(default=True)

	class Meta:
		ordering = ('created_at',)
		db_table = 'peekaboo_collection_comment'
		managed = True

	def __str__(self):
		return f'Comment by {self.name} on {self.collection}'
