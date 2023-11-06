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
import modelmysql
import commons


class FormSearchLogin(forms.Form):
    loginName = forms.CharField(
        label="Login Name",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Customer username ...",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=1,
        max_length=20,
        validators=[
            RegexValidator(
                regex="^[a-z0-9][a-z0-9.-]*[a-z0-9]$",
                message="invalid characters",
            )
        ],
    )
    latestDate = forms.CharField(
        label="Latest Date",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=1,
        max_length=20,
        initial=str(datetime.now().strftime("%Y-%m-%d")),
        validators=[
            RegexValidator(
                regex="^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
                message="invalid characters 0000-00-00",
            )
        ],
    )


def get_latest_connection(loginName=""):
    querySQL = """
        SELECT Max(InDate) AS 'MaxDate'
        FROM RadiusAcct
        WHERE UserName = %(loginName)s
        """
    paramSQL = {
        "loginName": loginName,
    }
    results = modelmysql.queryDBall(querySQL, paramSQL)
    return results


def get_month_stats(formSearchLogin, earlierMonth=0):
    latestDate = formSearchLogin.get("latestDate", "")
    startOfPeriod = latestDate[:-2] + "01"
    loginName = formSearchLogin.get("loginName", "")
    querySQL = """
    SELECT Date_Add( %(startOfPeriod)s,INTERVAL %(earlierMonth)s MONTH) AS 'StartOfPeriod',
        ifnull(sum(AcctSessionTime),0) / 3600 AS 'SessionTime',
        ifnull(sum(AcctInputOctets),0) / (1024*1024) AS 'TotAcctInputOctets',
        ifnull(sum(AcctOutputOctets),0) / (1024*1024) AS 'TotAcctOutputOctets'
    FROM RadiusAcct
    WHERE UserName = %(loginName)s
        AND InDate between Date_Add( %(startOfPeriod)s ,INTERVAL %(earlierMonth)s MONTH)
        AND Date_Add( %(startOfPeriod)s ,INTERVAL %(earlierMonth)s +1 MONTH)
        """
    paramSQL = {
        "startOfPeriod": startOfPeriod,
        "loginName": loginName,
        "earlierMonth": str(earlierMonth),
    }
    # print(f"DEBUG: querySQL: {querySQL}")
    # print(f"DEBUG: paramSQL: {paramSQL}")
    results = modelmysql.queryDBall(querySQL, paramSQL)
    # print(f"DEBUG: results: {results}")
    return results


def get_current_stats(formSearchLogin):
    loginName = formSearchLogin.get("loginName", "")
    querySQL = """
    SELECT InDate
        ,OutDate
        ,AcctSessionTime
        ,CallingStationId
        ,InitialConnectRate
        ,AcctTerminateCause
        ,NASIdentifier
        ,FramedIPAddress
        ,AcctInputOctets
        ,AcctOutputOctets
    FROM CurrentRadiusUsers
    WHERE UserName = %(loginName)s
    """
    paramSQL = {
        "loginName": loginName,
    }
    # print(f"DEBUG: querySQL: {querySQL}")
    # print(f"DEBUG: paramSQL: {paramSQL}")
    results = modelmysql.queryDBall(querySQL, paramSQL)
    # print(f"DEBUG: results: {results}")
    return results


def get_stats(formSearchLogin):
    loginName = formSearchLogin.get("loginName", "")
    latestDate = formSearchLogin.get("latestDate", "")
    querySQL = """
    SELECT InDate
        ,OutDate
        ,AcctSessionTime / 3600 AS 'AcctSessionTime'
        ,CallingStationId
        ,CalledStationId
        ,InitialConnectRate
        ,AcctTerminateCause
        ,NASIdentifier
        ,FramedIPAddress
        ,AcctInputOctets / (1024 * 1024) AS 'AcctInputOctets'
        ,AcctOutputOctets / (1024 * 1024) AS 'AcctOutputOctets'
    FROM RadiusAcct
    WHERE UserName = %(loginName)s
        AND InDate < Date_Add( %(latestDate)s ,INTERVAL +1 Day)
    ORDER BY OutDate DESC
    LIMIT 50
    """
    paramSQL = {
        "loginName": loginName,
        "latestDate": latestDate,
    }
    results = modelmysql.queryDBall(querySQL, paramSQL)
    # print(f"DEBUG: results: {results}")
    return results


def index(request):
    # get loginname from POST or from URL
    defaultData = {
        "loginName": request.POST.get("loginName")
        or request.GET.get("loginName")
        or request.GET.get("LoginName")
        or request.session.get("loginName")
        or "",
    }
    formSearchLogin = FormSearchLogin(initial=defaultData)
    #
    # pre assign parameters
    loginName = defaultData.get("loginName")
    monthStats = list()
    earlierMonthStats = list()
    currentStats = list()
    allStats = list()

    if request.method == "POST" and (request.POST.get("updateItemBTN")):
        formSearchLogin = FormSearchLogin(request.POST.dict())
        if formSearchLogin.is_valid():
            loginName = formSearchLogin.cleaned_data.get("loginName", "")
            confirmedLoginName = commons.get_loginname_from_database(loginName)
            loginName = confirmedLoginName
            if len(loginName) > 0:
                request.session["loginName"] = loginName
                latest_connection = get_latest_connection(loginName)
                monthStats = get_month_stats(formSearchLogin.cleaned_data, 0)
                earlierMonthStats = get_month_stats(formSearchLogin.cleaned_data, -1)
                currentStats = get_current_stats(formSearchLogin.cleaned_data)
                allStats = get_stats(formSearchLogin.cleaned_data)

    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formSearchLogin": formSearchLogin,
        "monthStats": monthStats,
        "earlierMonthStats": earlierMonthStats,
        "currentStats": currentStats,
        "allStats": allStats,
    }
    return render(request, "netstats/sample.html", context)
