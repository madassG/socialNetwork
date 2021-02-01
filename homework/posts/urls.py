from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path('<str:username>/<int:post_id>/edit', views.post_edit, name='edit_post'),
]