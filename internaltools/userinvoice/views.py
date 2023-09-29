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


def sanitizeLogin(loginName):
    loginSanitized = loginName if re.match(r"^[\w.-]{1,30}$", loginName) else ""
    return loginSanitized


def countConfirmedLoginName(loginToCheck):
    loginToCheckSanitized = sanitizeLogin(loginToCheck)
    loginFound = queryDBscalar(
        f"SELECT count(*) FROM UsersId where LoginName = lower('{loginToCheckSanitized}')"
    )
    return loginFound


def getInvoiceNumberFromInvoiceString(invoiceString=""):
    invoiceNumber = "0"
    #
    if str(invoiceString).isdecimal():
        invoiceNumber = str(invoiceString)
    #
    matchResult = re.match("^[0-9]{3}.([0-9]+)[0-9]{3}$", str(invoiceString))
    if matchResult:
        invoiceNumber = matchResult.group(1)
    #
    return invoiceNumber


def getLoginNameFromInvoiceNumber(invoiceNumber):
    invoiceNumberSanitized = sanitizeLogin(invoiceNumber)
    invoiceNumberDigits = getInvoiceNumberFromInvoiceString(invoiceNumberSanitized)
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


""" simpleCrypt encrypt/decrypt with XOR """


def simpleCrypt(varToCrypt=""):
    simpleCrypt = ""
    for i in range(len(varToCrypt) - 1, -1, -1):
        simpleCrypt = simpleCrypt + chr(ord(varToCrypt[i]) ^ 22)
    return simpleCrypt


def insertInvoiceKeys(userInvoices):
    for eachInvoice in userInvoices:
        loginName = eachInvoice.get("LoginName")
        loginNameCrypted = simpleCrypt(loginName)
        invoiceNumber = eachInvoice.get("InvoiceNumber")
        if isinstance(invoiceNumber, int):
            invoiceNumberCrypted = simpleCrypt(str(invoiceNumber))
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
        "loginName": request.GET.get("loginName") or "",
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
            # messages.add_message( request, messages.SUCCESS, f"Found User {loginName}")
            invoices["UserInvoice"] = getInvoices(loginName)
            invoices["UniqueInvoices"] = getUniqueInvoices(invoices["UserInvoice"])
            invoices["InvoiceDetail"] = getInvoicesDetail(invoices["UniqueInvoices"])
            invoices["UserPlans"] = getUserPlans(loginName)
            insertInvoiceKeys(invoices["UserInvoice"])

    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "buttonStyle": "success" if isUserExist else "secondary",
        "isValid": "isValid" if isUserExist else "is-invalid",
        "isDisabled": "" if isUserExist else "disabled",
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formSearchLogin": formSearchLogin,
        "invoices": invoices,
        "loginNameCrypted": simpleCrypt(loginName),
    }
    return render(request, "userinvoice/sample.html", context)
