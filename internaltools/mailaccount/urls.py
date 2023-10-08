from django.urls import path

from . import views

app_name = "mailaccount"
urlpatterns = [
    path('', views.index, name='index'),
]
