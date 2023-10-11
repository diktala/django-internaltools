from django.urls import path

from . import views

app_name = "endaccount"
urlpatterns = [
    path('', views.index, name='index'),
]
