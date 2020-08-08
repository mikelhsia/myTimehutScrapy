from django.shortcuts import render, get_object_or_404
from .models import PeekabooCollection, PeekabooMoment, PeekabooCollectionComment, Profile, User, Contact
from actions.models import Action

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .form import EmailCollectionForm, CommentForm, LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from django.core.mail import send_mail

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from myTimehutBlog.common.decorators import ajax_required

from django.contrib import messages

from actions.utils import create_action

# This class-based view is analogous to the previous post_list view.
class CollectionView(ListView):
	'''
		- Use a specific queryset instead of retrieving all objects. Instead of defining a queryset attribute, we could
		have specified model = Post and Django would have built the generic Post.objects.all() queryset for us.
		- Use the context variable posts for the query results. The default variable is object_list if we don't specify any context_object_name.
		- Paginate the result displaying three objects per page.
		- Use a custom template to render the page. If we don't set a default template, ListView will use blog/post_list.html.”
	'''
	queryset = PeekabooCollection.objects.all()
	context_object_name = 'collections'
	paginate_by = 5
	template_name = 'collection/collection_list.html'

# Create your views here.
@login_required
def collection_list(request):
	collection_list = PeekabooCollection.objects.all()

	# 10 collection per page
	paginator = Paginator(collection_list, 10)

	# We get the page GET parameter that indicates the current page number.
	page = request.GET.get('page')
	try:
		collections = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer deliver the first page
		collections = paginator.page(1)
	except EmptyPage:
		# If page is out of range deliver last page of result
		collections = paginator.page(paginator.num_pages)

	# thumbnails = [PeekabooMoment.objects.filter(event=x.id)[0].src_url for x in collections]
	# return render(request, 'collection/collection_list.html', {'page': page, 'collections': collections, 'thumbnails': thumbnails})

	return render(request, 'collection/collection_list.html', {'page': page, 'collections': collections, 'section': 'album'})

@login_required
def collection_detail(request, collection_id):
	collection = get_object_or_404(PeekabooCollection, id=collection_id)
	moment_list = PeekabooMoment.objects.filter(event=collection_id)

	# List of active comments for this collection
	comments = collection.comments.filter(active=True)

	if request.method == 'POST':
		# A comment is going to be posted
		comment_form = CommentForm(data=request.POST)
		if comment_form.is_valid():
			# Create Comment object but don't save to database
			new_comment = comment_form.save(commit=False)
			# Assign collection to the comment
			new_comment.collection = collection
			# Save comment
			new_comment.save()

			# Clean the form after the data is saved
			comment_form = CommentForm()
	else:
		comment_form = CommentForm()

	return render(request, 'collection/collection_detail.html', {'collection': collection, 'moment_list': moment_list,
	                                                             'comments': comments, 'comment_form': comment_form,
	                                                             'section': 'album'})

@login_required
def collection_share(request, collection_id):
	# Retrieve collection by id
	collection = get_object_or_404(PeekabooCollection, id=collection_id)
	sent = False

	if request.method == 'POST':
		# Form was submitted
		form = EmailCollectionForm(request.POST)

		if form.is_valid():
			# Form fields passed validation
			cd = form.cleaned_data

			# ... send email
			# collection_url = request.build_absolute_uri(collection.get_absolute_url())
			subject = f"{cd['name']} ({cd['email']}) recommends you reading {collection.id}"
			message = f"{collection.caption}"
			send_mail(subject, message, 'admin@myblog.com', [cd['to']])
			sent = True
	else:
		form = EmailCollectionForm()

	return render(request, 'collection/share.html', {'collection': collection, 'form': form, 'sent': sent,
	                                                 'section': 'album'})


# -------------------------------------------------------
# Login view: Now obsolete since using default auth.views
def user_login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)

		if form.is_valid():
			cd = form.cleaned_data

			# This method takes a username and a password and returns a User object if the user has
			# been successfully authenticated, or None otherwise. If the user has not been authenticated,
			# we return a raw HttpResponse displaying a message.
			user = authenticate(username=cd['username'], password=cd['password'])

			if user is not None:
				# We check if user is an active user
				if user.is_active:
					login(request, user)

					# We return a raw HttpResponse to display a message
					return HttpResponseRedirect('/blog/collection')
				else:
					return HttpResponse('Disabled account')
			else:
				return HttpResponse('Invalid login')

	else:
		form = LoginForm()

	return render(request, 'account/login.html', {'form': form})

# -------------------------------------------------------
# Login template view

# The login_requred decorator checks if the current user is authenticated
# if the user is authenticated, it executes the decorated view
# if the user is not authenticated, it redirects him to the login URL with
# the URL he was trying to access as a GET param named 'next'. Remember to add hidden input in the form
@login_required
def dashboard(request):
	# Display all actions by default

	actions = Action.objects.exclude(user=request.user)
	followings_ids = request.user.following.values_list('id', flat=True)

	if followings_ids:
		# If user is following others, retrieve only their actions
		actions = actions.filter(user_id__in=followings_ids).select_related('user', 'user__profile').prefetch_related('target')
		# actions = actions.filter(user_id__in=followings_ids)
		actions = actions[:10]

	return render(request, 'registration/dashboard.html', {'section': 'dashboard', 'actions': actions})


def register(request):
	if request.method == 'POST':
		user_form = UserRegistrationForm(request.POST)
		if user_form.is_valid():
			new_user = user_form.save(commit=False)
			new_user.set_password(user_form.cleaned_data['password'])
			new_user.save()
			profile = Profile.objects.create(user=new_user)
			create_action(new_user, 'has created an account')

			# Create the user profile
			profile = Profile.objects.create(user=new_user)
			return render(request, 'registration/register_done.html', {'new_user': new_user})
	else:
		user_form = UserRegistrationForm()
	return render(request, 'registration/register.html', {'user_form': user_form})

@login_required
def edit(request):
	if request.method == 'POST':
		user_form = UserEditForm(instance=request.user, data=request.POST)
		profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)

		if user_form.is_valid() and profile_form.is_valid():
			user_form.save()
			profile_form.save()
			messages.success(request, 'Profile updated successfully')
		else:
			messages.error(request, 'Error updating your profile')
	else:
		user_form = UserEditForm(instance=request.user)
		profile_form = ProfileEditForm(instance=request.user.profile)

	return render(request, 'registration/edit.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
def user_list(request):
	users = User.objects.filter(is_active=True)

	return render(request, 'user/list.html', {'section': 'people', 'users': users})


@login_required
def user_detail(request, username):
	user = get_object_or_404(User, username=username, is_active=True)

	return render(request, 'user/detail.html', {'section': 'people', 'user': user})

@require_POST
@ajax_required
@login_required
def user_follow(request):
	user_id = request.POST.get('id')
	action = request.POST.get('action')

	if user_id and action:
		try:
			user = User.objects.get(id=user_id)
			if action == 'follow':
				Contact.objects.get_or_create(user_from=request.user, user_to=user)
				create_action(request.user, 'is following', user)
			else:
				Contact.objects.filter(user_from=request.user, user_to=user).delete()
			return JsonResponse({'status': 'ok'})
		except User.DoesNotExist:
			return JsonResponse({'status': 'ko'})

	return JsonResponse({'status': 'ko'})
