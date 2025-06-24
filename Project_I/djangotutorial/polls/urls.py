from django.urls import path

from . import views


app_name = "polls"
urlpatterns = [
    # the 'name' value as called by the  {% url %} template tag
    path("", views.IndexView.as_view(), name="index"),
    path("<question_id>/shm/", views.shmindex, name="shmindex"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
]