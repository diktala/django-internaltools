from django.urls import path

from . import views

app_name = "userinvoice"
urlpatterns = [
    path('', views.index, name='index'),
]
