from django.contrib.sitemaps import Sitemap
from .models import PeekabooCollection, PeekabooMoment

from datetime import datetime

'''
Django comes with a sitemap framework, which allows you to generate sitemaps for
your site dynamically. A sitemap is an XML file that tells search engines the pages
of your website, their relevance, and how frequently they are updated. By using a
sitemap, you will help crawlers indexing your website's content.
'''

def timestampToDatetime(ts):
	"""
	Convert timestamp into string with datetime format
	:param ts: timestamp
	:return: datetime string
	"""
	if isinstance(ts, (int, float, str)):
		try:
			ts = int(ts)
		except ValueError:
			raise ValueError

		if len(str(ts)) == 13:
			ts = int(ts / 1000)
		if len(str(ts)) != 10:
			raise ValueError
	else:
		raise ValueError

	return datetime.fromtimestamp(ts)

class CollectionSitemap(Sitemap):
	changefreq = 'weekly'		# Change frequency of the collection
	priority = 0.9				# Relevance in the website

	def items(self):
		# By default, Django calls the get_absolute_url() method on each object to retrieve its URL
		return PeekabooCollection.objects.all()

	def lastmod(self, obj):
		return timestampToDatetime(obj.updated_at)