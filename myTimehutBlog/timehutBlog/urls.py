"""
urls.py for this application
"""

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

# Generating Card feed format
from .feeds import LatestCollectionsFeed

app_name = 'timehutBlog'
urlpatterns = [
	# Old custom login view
	# path('login/', views.user_login, name='login'),

	# New login page
	path('', views.dashboard, name='dashboard'),

	# login/logout urls
	path('login/', auth_views.login, name='login'),
	# Use as_view to pass template name to the view
	path('logout/', auth_views.LogoutView.as_view(template_name='registration/logged_user_out.html'), name='logout'),
	path('logout-then-login/', auth_views.logout_then_login, name='logout_then_login'),

	# Change password urls
	path('password-change/', auth_views.PasswordChangeView.as_view(template_name='registration/user_password_change_form.html',
	                                                               success_url=reverse_lazy('timehutBlog:password_change_done')),
	     name='password_change'),
	path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/user_password_change_done.html'),
	     name='password_change_done'),

	# Restore password urls
	path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/user_password_reset_form.html',
	                                                             email_template_name='registration/user_password_reset_email.html',
	                                                             success_url=reverse_lazy('timehutBlog:password_reset_done')),
	     name='password_reset'),
	path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/user_password_reset_done.html'),
	     name='password_reset_done'),
	path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/user_password_reset_confirm.html',
	                                                                                             success_url=reverse_lazy('timehutBlog:password_reset_complete')),
	     name='password_reset_confirm'),
	path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/user_password_reset_complete.html'),
	     name='password_reset_complete'),

	# blog/collection
	path('collection/', views.collection_list, name='collection_list'),
	path('collection/<int:collection_id>/', views.collection_detail, name='collection_detail'),
	path('collection/<int:collection_id>/share/', views.collection_share, name='collection_share'),
	path('feed/', LatestCollectionsFeed(), name='collection_feed'),

	# Registration
	path('register/', views.register, name='register'),

	# Edit user and profile
	path('edit/', views.edit, name='edit'),

	# User followers
	path('users/', views.user_list, name='user_list'),
	path('users/follow/', views.user_follow, name='user_follow'),
	path('users/<username>/', views.user_detail, name='user_detail'),
]
