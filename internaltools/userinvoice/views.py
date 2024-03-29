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


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


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


def countConfirmedLoginName(loginToCheck):
    loginToCheckSanitized = commons.sanitizeLogin(loginToCheck)
    loginFound = queryDBscalar(
        f"SELECT count(*) FROM UsersId where LoginName = lower('{loginToCheckSanitized}')"
    )
    return loginFound


def getLoginNameFromInvoiceNumber(invoiceNumber):
    invoiceNumberSanitized = commons.sanitizeLogin(invoiceNumber)
    invoiceNumberDigits = commons.get_invoicenumber_from_obfuscated_number(
        invoiceNumberSanitized
    )
    loginName = queryDBscalar(
        f"SELECT LoginName FROM Invoices where InvoiceNumber = %s",
        str(invoiceNumberDigits),
    )
    if isinstance(loginName, str):
        return loginName.strip()
    else:
        return ""


""" search loginName in the database """


def getConfirmedLoginName(loginName=""):
    confirmedLoginName = ""
    """ case loginname is an invoicenumber """
    loginNameFromInvoice = getLoginNameFromInvoiceNumber(loginName)
    loginFound = countConfirmedLoginName(loginNameFromInvoice)
    if str(loginFound) == "1":
        confirmedLoginName = loginNameFromInvoice

    """ case loginname is normal alias """
    loginFound = countConfirmedLoginName(loginName)
    if str(loginFound) == "1":
        confirmedLoginName = loginName

    return confirmedLoginName


def getInvoices(loginName):
    # invoices["UserInvoice"] = _getUserInvoice(loginName)
    # invoices["UserInvoiceDetail"] = _getUserInvoiceDetail(loginName)
    # invoices["UserPlans"] = _getUserPlans(loginName)
    allRows = None
    try:
        aladinSQL1 = f"""
            EXECUTE UserInvoice
            @LoginName = %(loginName)s
            """
        aladinParam1 = {
            "loginName": loginName,
        }
        allRows = queryDBall(aladinSQL1, aladinParam1)
    except Exception as error:
        pass
    return allRows


""" returns "list" of unique invoices used by user  """


def getUniqueInvoices(userInvoices):
    invoiceNumbers = set([])
    for eachRow in userInvoices:
        invoice = eachRow.get("InvoiceNumber")
        if invoice:
            invoiceNumbers.add(invoice)
    return invoiceNumbers


""" get invoicedetail for each invoice """


def getInvoicesDetail(invoiceNumbers):
    userInvoicesDetail = {}
    for eachInvoiceNumber in invoiceNumbers:
        allRows = None
        try:
            aladinSQL1 = f"""
                EXECUTE UserInvoiceDetail
                @InvoiceNumber = %s
                """
            aladinParam1 = (eachInvoiceNumber,)
            allRows = queryDBall(aladinSQL1, aladinParam1)
            userInvoicesDetail[eachInvoiceNumber] = allRows
        except Exception as error:
            pass
    return userInvoicesDetail


""" get UsersPlans from database """


def getUserPlans(loginName=""):
    allRows = []
    try:
        aladinSQL1 = f"""
            EXECUTE UpdateUsersPlans
            @LoginName = %s
            """
        aladinParam1 = loginName or " "
        allRows = queryDBall(aladinSQL1, aladinParam1)
    except Exception as error:
        pass
    return allRows


def insertInvoiceKeys(userInvoices):
    for eachInvoice in userInvoices:
        loginName = eachInvoice.get("LoginName")
        loginNameCrypted = commons.simpleCrypt(loginName)
        invoiceNumber = eachInvoice.get("InvoiceNumber")
        if isinstance(invoiceNumber, int):
            invoiceNumberCrypted = commons.simpleCrypt(str(invoiceNumber))
            invoiceObfuscated = (
                str((invoiceNumber**0.5) * 1000000)[0:3]
                + "."
                + str(invoiceNumber)
                + str((invoiceNumber**0.5) * 1000000)[3:6]
            )
            eachInvoice["invoiceNumberCrypted"] = invoiceNumberCrypted
            eachInvoice["invoiceNumberObfuscated"] = invoiceObfuscated
        eachInvoice["loginNameCrypted"] = loginNameCrypted


def index(request):
    defaultData = {
        "loginName": request.GET.get("loginName")
        or request.session.get("loginName")
        or "",
    }
    formSearchLogin = FormSearchLogin(defaultData)
    loginName = defaultData.get("loginName")
    isUserExist = False
    invoices = dict()

    """ GET request received """
    if formSearchLogin.is_valid():
        loginName = formSearchLogin.cleaned_data["loginName"]
        confirmedLoginName = getConfirmedLoginName(loginName)
        if confirmedLoginName:
            isUserExist = True
            loginName = confirmedLoginName
            # store loginName in session cookie
            request.session["loginName"] = loginName
            # messages.add_message( request, messages.SUCCESS, f"Found User {loginName}")
            invoices["UserInvoice"] = getInvoices(loginName)
            invoices["UniqueInvoices"] = getUniqueInvoices(invoices["UserInvoice"])
            invoices["InvoiceDetail"] = getInvoicesDetail(invoices["UniqueInvoices"])
            invoices["UserPlans"] = getUserPlans(loginName)
            insertInvoiceKeys(invoices["UserInvoice"])

    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formSearchLogin": formSearchLogin,
        "invoices": invoices,
        "loginNameCrypted": commons.simpleCrypt(loginName),
    }
    return render(request, "userinvoice/sample.html", context)
