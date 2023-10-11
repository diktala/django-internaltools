from django.urls import path

from . import views

app_name = "restoreuser"
urlpatterns = [
    path('', views.index, name='index'),
]
