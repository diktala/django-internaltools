from django.urls import path

from . import views

app_name = "conndebug"
urlpatterns = [
    path('', views.index, name='index'),
]
