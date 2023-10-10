# django-internaltools
django crud to manage users

---

- Quick start an app:

```
# make sure venv is active
python -m venv ~/venv
source ~/venv/bin/activate

# 
cd ~/django-internaltools/internaltools/
python manage.py startapp userplans

# ~/django-internaltools/internaltools/settings.py
|INSTALLED_APPS = [
 ...
 'userplans.apps.UserplansConfig',
]

# ~/django-internaltools/internaltools/urls.py
urlpatterns = [
   ...
    path('userplans/', include('userplans.urls')),
]

# create: ~/django-internaltools/internaltools/userplans/urls.py
from django.urls import path

from . import views

app_name = "userplans"
urlpatterns = [
    path('', views.index, name='index'),
]

# ~/django-internaltools/internaltools/userplans/views.py
from django.http import HttpResponse
def index(request):
    return HttpResponse("Hello, world.")

# ~/django-internaltools/internaltools/templates/internaltools/topmenu.html
{% url 'userplans:index' as thisurl %}
<a class="nav-link p-0 {% if request.path == thisurl %}active{% endif %}"
href="{{ thisurl }}">Info User</a>

# templates
mkdir -p ~/django-internaltools/internaltools/userplans/templates/userplans/

```
