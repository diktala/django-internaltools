from django.urls import path

from . import views

app_name = "billinglist"
urlpatterns = [
    path('', views.index, name='index'),
]
