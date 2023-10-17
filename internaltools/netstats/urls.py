from django.urls import path

from . import views

app_name = "netstats"
urlpatterns = [
    path('', views.index, name='index'),
]
