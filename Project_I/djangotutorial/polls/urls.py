from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("shm", views.shmindex, name="shmindex"),
    path("<int:question_id>/", views.detail, name="detail"),
    path("<int:question_id>/results/", views.results, name="resutls"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
]