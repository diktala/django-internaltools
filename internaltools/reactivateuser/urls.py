from django.urls import path

from . import views

app_name = "reactivateuser"
urlpatterns = [
    path('', views.index, name='index'),
]
