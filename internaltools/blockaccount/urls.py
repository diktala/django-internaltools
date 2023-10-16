from django.urls import path

from . import views

app_name = "blockaccount"
urlpatterns = [
    path('', views.index, name='index'),
]
