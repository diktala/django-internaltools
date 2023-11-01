from django.urls import path

from . import views

app_name = "sendmail"
urlpatterns = [
    path('', views.index, name='index'),
]
