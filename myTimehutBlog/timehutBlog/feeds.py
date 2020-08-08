from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from .models import PeekabooCollection

'''
Django has a built-in syndication feed framework that you can use to dynamically
generate RSS or Atom feeds in a similar manner to creating sitemaps using the
sites framework.
'''

class LatestCollectionsFeed(Feed):
	title = 'Hsia\'s timehut'
	link = '/blog/collection'
	description = 'New collection from Hsia\'s timehut'

	def items(self):
		return PeekabooCollection.objects.all()[:5]

	def item_title(self, item):
		if item.baby_id == '537413380':
			title = 'Anson'
		else:
			title = 'Angie'
		return f'{title} - {item.months} months | {item.days} days' 

	def item_description(self, item):
		return truncatewords(item.caption, 20)