from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
import datetime


def index(request):
    now = datetime.datetime.now()
    html_start = "<html><body>"
    html = "It is now %s. <br />" % now
    html += f"HTTP_X_FORWARDED_FOR: {request.META.get('HTTP_X_FORWARDED_FOR')} <br />"
    html += f"HTTP_X_REAL_IP: {request.META.get('HTTP_X_REAL_IP')} <br />"
    html += f"REMOTE_ADDR: {request.META.get('REMOTE_ADDR')} <br />"
    html_end = "</body></html>"
    return HttpResponse(f"{html_start} {html} {html_end}")
