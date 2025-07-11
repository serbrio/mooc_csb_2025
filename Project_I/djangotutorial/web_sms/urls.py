from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views


app_name = "web_sms"
urlpatterns = [
    # the 'name' value as called by the  {% url %} template tag
    path("", views.homePageView, name="index"),
    path("send_message/", views.sendView),
    path("logout/", LogoutView.as_view(next_page='/web_sms/')),
    path("delete_message/", views.deleteView),
    path("<message_id>/read_message/", views.showMessageView, name="read_message"),
    ## Fix Flaw 4
    ## The next three lines to be commented-out for the fix.
    path("recover_password/", views.recoverPasswordView, name="recover_password"),
    path("<username>/secret_question/", views.secretQuestionView, name="secret_question"),
    path("<username>/password_change/", views.passwordChangeView, name="password_change"),
    ## End Fix Flaw 4
]