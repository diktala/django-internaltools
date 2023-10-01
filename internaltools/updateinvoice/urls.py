from django.urls import path

from . import views

app_name = "updateinvoice"
urlpatterns = [
    path('', views.index, name='index'),
]
