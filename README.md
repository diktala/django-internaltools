# django-internaltools
django crud to manage users

---

- Dev environement

```
iterm2 with 3 tabs each with screen session:
:sessionname docker
:sessionname s2
:sessionname s3
screen -d -r s docker
    0$ -> docker-compose up -d; docker-compose logs -f
    1$ -> docker container exec -it --user squid devtools bash
       -> source ~/django-internaltools/venv/bin/activate
       -> cd ~/django-internaltools/internaltools/
       -> python manage.py shell
       -> import some-app.views
screen -d -r s s2
screen -d -r s s3

```

- Quick start an app:

```
# make sure venv is active
source venv/bin/activate

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

- update production instance

```
docker container exec -it --user=squid internaltools bash
cd ~/django-internaltools/; git pull; killall -HUP gunicorn
```
