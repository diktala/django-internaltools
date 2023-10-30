from django.urls import path

from . import views

app_name = "connectlocator"
urlpatterns = [
    path('', views.index, name='index'),
]
