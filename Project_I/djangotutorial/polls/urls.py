from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("shm", views.shmindex, name="shmindex"),
]