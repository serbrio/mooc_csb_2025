from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views


app_name = "web_sms"
urlpatterns = [
    # the 'name' value as called by the  {% url %} template tag
    path("", views.homePageView, name="index"),
    #path("register/", views.registerView),
    path("send_message/", views.sendView),
    #path("login/", LoginView.as_view(template_name="login.html")),
    path("logout/", LogoutView.as_view(next_page='/web_sms/')),
    path("delete_message/", views.deleteView),
]