from django.urls import path

from . import views

app_name = "userinput"
urlpatterns = [
    path('', views.index, name='index'),
]
