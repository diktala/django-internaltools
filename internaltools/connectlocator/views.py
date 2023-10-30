import os
import re
from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib import messages
import commons
import modelmysql


class FormConnections(forms.Form):
    searchTerm = forms.CharField(
        label="Search Term",
        widget=forms.TextInput(
            attrs={
                "placeholder": "... search any user or ip ...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=4,
        max_length=20,
        validators=[
            RegexValidator(
                regex="^[A-Za-z0-9.-]*$",
                message="invalid characters",
            )
        ],
    )
    lastDays = forms.DecimalField(
        label="Search Days",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        max_digits=2,
        decimal_places=0,
    )


def get_user_connection(searchTerm="", lastDays=""):
    # notice if searchTerm is empty return everything
    if not searchTerm:
        searchTerm = ""
    if not lastDays:
        lastDays = 30
    limitRecords = 400
    querySQL = f"""
        (
        SELECT OutDate
            ,InDate
            ,UserName
            ,NASIdentifier
            ,CallingStationId
            ,FramedIPAddress
            ,(AcctSessionTime / 3600) AS 'ConnectionInHours'
            ,AcctTerminateCause
            ,AcctSessionId
        FROM RadiusAcct
        WHERE OutDate >= DATE_SUB(now(),INTERVAL {lastDays} DAY)
            AND (
                UserName = %(searchTerm)s
                OR FramedIpAddress = %(searchTerm)s
                OR NASIdentifier = %(searchTerm)s
                OR CallingStationId = %(searchTerm)s
                OR FramedIPAddress = %(searchTerm)s
                OR AcctTerminateCause = %(searchTerm)s
                OR AcctSessionId = %(searchTerm)s
                OR "" = %(searchTerm)s
            )
        ORDER BY InDate DESC
        LIMIT {limitRecords}
        )
        UNION
        (
        SELECT OutDate
            ,InDate
            ,UserName
            ,NASIdentifier
            ,CallingStationId
            ,FramedIPAddress
            ,(AcctSessionTime / 3600) AS 'ConnectionInHours'
            ,AcctTerminateCause
            ,AcctSessionId
        FROM CurrentRadiusUsers
        WHERE InDate >= DATE_SUB(now(),INTERVAL {lastDays} DAY)
            AND (
                UserName = %(searchTerm)s
                OR FramedIpAddress = %(searchTerm)s
                OR NASIdentifier = %(searchTerm)s
                OR CallingStationId = %(searchTerm)s
                OR FramedIPAddress = %(searchTerm)s
                OR AcctTerminateCause = %(searchTerm)s
                OR AcctSessionId = %(searchTerm)s
                OR "" = %(searchTerm)s
            )
        ORDER BY InDate DESC
        LIMIT {limitRecords}
        )
        ORDER BY InDate DESC
        """
    paramSQL = {
        "searchTerm": searchTerm,
        "lastDays": lastDays,
    }
    # print(f"DEBUG: querySQL: {querySQL}")
    # print(f"DEBUG: paramSQL: {paramSQL}")
    results = modelmysql.queryDBall(querySQL, paramSQL)
    return results


def index(request):
    # get loginName from session cookie. used for topmenu only
    loginName = request.session.get("loginName", "")
    #
    defaultSearchTerm = (
        request.GET.get("loginName") or request.GET.get("LoginName") or ""
    )
    defaultLastDays = 30
    defaultData = {
        "searchTerm": defaultSearchTerm,
        "lastDays": defaultLastDays,
    }
    formConnections = FormConnections(initial=defaultData)
    userConnection = list()
    #
    if request.method == "POST":
        formConnections = FormConnections(request.POST.dict())
        if formConnections.is_valid():
            searchTerm = formConnections.cleaned_data.get("searchTerm")
            lastDays = formConnections.cleaned_data.get("lastDays")
            userConnection = get_user_connection(searchTerm, lastDays)

    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formConnections": formConnections,
        "userConnection": userConnection,
    }
    return render(request, "connectlocator/sample.html", context)
