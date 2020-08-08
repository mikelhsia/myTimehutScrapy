from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm
from .models import Image

from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST

from myTimehutBlog.common.decorators import ajax_required

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from actions.utils import create_action

import redis
from django.conf import settings

# Connect to redis
r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB)

# Create your views here.
@login_required
def image_create(request):
	if request.method == 'POST':
		# form is sent
		form = ImageCreateForm(data=request.POST)

		if form.is_valid():
			# form data is valid
			cd = form.cleaned_data
			new_item = form.save(commit=False)

			# assign current user to the item
			new_item.user = request.user
			new_item.save()
			create_action(request.user, 'bookmarked image', new_item)

			messages.success(request, 'Image added successfully')

			# redirect to new created item detail view
			return redirect(new_item.get_absolute_url())

	else:
		# build form with data provided by the bookmarklet via GET
		form = ImageCreateForm(data=request.GET)

	return render(request, 'images/image/create.html', {'section': 'images', 'form': form})


def image_detail(request, id, slug):
	image = get_object_or_404(Image, id=id, slug=slug)

	# increment total image views by 1
	# and we build the Redis key by using notation by object-type:id:field (for ex: image:33:id)
	total_views = r.incr(f'image:{image.id}:views')

	# increment image ranking by 1
	# We use the zincrby() to store image views in a sorted set with the key image:ranking
	# Storing the image id, and a scor of 1 that will be added to the total score of this element in the sorted set
	r.zincrby('image_ranking', image.id, 1)

	return render(request, 'images/image/detail.html', {'section': 'images', 'image': image, 'total_views': total_views})


@login_required
def image_list(request):
	images = Image.objects.all()
	paginator = Paginator(images, 8)
	page = request.GET.get('page')

	try:
		images = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer deliver the first page
		images = paginator.page(1)
	except EmptyPage:
		if request.is_ajax():
			# If the request is AJAX and the page is out of range
			# return an empty page
			return HttpResponse('')
		images = paginator.page(paginator.num_pages)

	if request.is_ajax():
		return render(request, 'images/image/list_ajax.html', {'section': 'images', 'images': images})

	return render(request, 'images/image/list.html', {'section': 'images', 'images': images})

# The require_POST decorator returns an HttpResponseNotAllowed object (status code 405) if the HTTP request is not done via POST.
@ajax_required
@login_required
@require_POST
def image_like(request):
	image_id = request.POST.get('id')
	action = request.POST.get('action')
	if image_id and action:
		try:
			image = Image.objects.get(id=image_id)

			# add() passing an object that is already present in the related object set does not duplicate it and thus
			# remove() passing an object that is not in the related object set does nothing
			# Another many-to-many manager is clear(), which removes all objects from the related object set
			if action == 'like':
				image.users_like.add(request.user)
				create_action(request.user, 'likes', image)
			else:
				image.users_like.remove(request.user)

			# JsonResponse class provided by Django, which returns an HTTP response with an application/json content type,
			# converting the given object into a JSON output.
			return JsonResponse({'status': 'ok'})
		except:
			pass
	return JsonResponse({'status': 'ko'})

@login_required
def image_ranking(request):
	# get image ranking dictionary
	image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
	image_ranking_ids = [int(id) for id in image_ranking]

	# get most viewed images
	most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
	most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))

	return render(request, 'images/image/ranking.html', {'section': 'images', 'most_viewed': most_viewed})