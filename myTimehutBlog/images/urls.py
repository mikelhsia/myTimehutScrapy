from django.urls import path, include
from . import views

# http://127.0.0.1:8000/images/create/?title=%20Django%20and%20Duke&url=http://upload.wikimedia.org/wikipedia/commons/8/85/Django_Reinhardt_and_Duke_Ellington_%28Gottlie

app_name = 'images'
urlpatterns = [
	path('create/', views.image_create, name='create'),
	path('detail/<int:id>/<slug>/', views.image_detail, name='detail'),
	path('like/', views.image_like, name='like'),
	# path('ranking/', views.image_ranking, name='create'),
	path('ranking/', views.image_ranking, name='ranking'),
	path('', views.image_list, name='list'),
]
