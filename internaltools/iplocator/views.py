from datetime import datetime, timedelta
import os
import re
from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib import messages
from modelmssql import queryDBall, queryDBrow, queryDBscalar
from django.template.defaulttags import register
import commons
import modelmysql
from dns import resolver


class FormLocateIP(forms.Form):
    ipAddress = forms.GenericIPAddressField(
        label="IP Address",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=True,
        protocol="IPv4",
    )
    accessDate = forms.DateTimeField(
        label="Access Date",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
    )


def get_user_connection(ipAddress="", accessDate=""):
    if not accessDate:
        accessDate = datetime.now().strftime("%Y-%m-%d %H:%M")
    querySQL = """
        SELECT UserName, InDate, OutDate
            ,(AcctSessionTime / 3600) AS 'ConnectionInHours'
            , CallingStationId
        FROM RadiusAcct
        WHERE FramedIpAddress= %(ipAddress)s
              AND OutDate >= %(dateMin)s
              AND InDate <= %(dateMax)s
        UNION
        SELECT UserName, InDate, OutDate
            , 0 , CallingStationId
        FROM CurrentRadiusUsers
        WHERE FramedIPAddress= %(ipAddress)s
              AND InDate <= %(dateMax)s
        """
    paramSQL = {
        "ipAddress": ipAddress,
        "dateMin": accessDate,
        "dateMax": accessDate,
    }
    # print(f"DEBUG: querySQL: {querySQL}")
    # print(f"DEBUG: paramSQL: {paramSQL}")
    results = modelmysql.queryDBall(querySQL, paramSQL)
    return results


def get_mac_from_ptr(ptr=""):
    mac = ""
    mac = re.sub(r"^.*-CM([A-Fa-f0-9]+).*$", r"\1", ptr)
    return mac


def get_cable_mac_from_ip(ip=""):
    # host -t ptr 104.37.80.107 24.201.245.207
    nameserver = "24.201.245.207"
    ns = resolver.Resolver()
    ns.nameservers = [nameserver]
    ns.timeout = 1
    ns.lifetime = 1
    output = ""
    try:
        result = ns.resolve_address(ip)
        output = result[0].to_text()
    except resolver.NoNameservers:
        pass
    return output


def index(request):
    # get loginName from session cookie. used for topmenu only
    loginName = request.session.get("loginName", "")
    #
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    defaultData = {
        "accessDate": now,
    }
    formLocateIP = FormLocateIP(initial=defaultData)
    userConnection = list()
    cableConnection = ""
    cableMac = ""
    #
    if request.method == "POST":
        formLocateIP = FormLocateIP(request.POST.dict())
        if formLocateIP.is_valid():
            ipAddress = formLocateIP.cleaned_data.get("ipAddress")
            accessDate = formLocateIP.cleaned_data.get("accessDate")
            userConnection = get_user_connection(ipAddress, accessDate)
            cableConnection = get_cable_mac_from_ip(ipAddress)
            cableMac = get_mac_from_ptr(cableConnection)

    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formLocateIP": formLocateIP,
        "userConnection": userConnection,
        "cableConnection": cableConnection,
        "cableMac": cableMac,
    }
    return render(request, "iplocator/sample.html", context)
