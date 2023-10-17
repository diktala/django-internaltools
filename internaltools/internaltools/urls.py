"""internaltools URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('updateuser/', include('updateuser.urls')),
    path('createuser/', include('createuser.urls')),
    path('userinvoice/', include('userinvoice.urls')),
    path('updateinvoice/', include('updateinvoice.urls')),
    path('userplans/', include('userplans.urls')),
    path('infouser/', include('infouser.urls')),
    path('', include('infouser.urls', namespace='generic')),
    path('mailaccount/', include('mailaccount.urls')),
    path('usersearch/', include('usersearch.urls')),
    path('outstandingissues/', include('outstandingissues.urls')),
    path('endaccount/', include('endaccount.urls')),
    path('restoreuser/', include('restoreuser.urls')),
    path('changepass/', include('changepass.urls')),
    path('userinput/', include('userinput.urls')),
    path('blockaccount/', include('blockaccount.urls')),
    path('commentlogs/', include('commentlogs.urls')),
    path('netstats/', include('netstats.urls')),
]

urlpatterns += staticfiles_urlpatterns()
