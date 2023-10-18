from datetime import datetime, timedelta
import os
import re
from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib import messages
from django.template.defaulttags import register
from modelmssql import queryDBall, queryDBrow, queryDBscalar
import modelmysql2
import commons


def get_connection_debugging():
    querySQL = """
        SELECT *
        FROM LastLogons
        WHERE LogDate > Date_Add(now(), INTERVAL - 600 minute)
        ORDER BY LogDate DESC
        LIMIT 1000
    """
    queryPARAM = {}
    # print(f"DEBUG MESSAGE: {querySQL}")
    # print(f"DEBUG MESSAGE: {queryPARAM}")
    result = modelmysql2.queryDBall(querySQL, queryPARAM)
    return result


def index(request):
    loginName = request.session.get("loginName")

    connectionList = get_connection_debugging()
    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "connectionList": connectionList,
    }
    return render(request, "conndebug/sample.html", context)
