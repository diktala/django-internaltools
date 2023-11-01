from datetime import datetime, timedelta
import os
import re
from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib import messages
from django.utils.http import urlencode
from django.template.defaulttags import register
from modelmssql import queryDBall, queryDBrow, queryDBscalar
import commons


def get_billing_list():
    querySQL = """
        SET ROWCOUNT 500;
        SELECT * FROM DelinquentAccounts WHERE Balance > %(balance)d; 
        SET ROWCOUNT 0;
    """
    queryPARAM = {
        "balance": 1.0,
    }
    result = queryDBall(querySQL, queryPARAM)
    return result


def extract_email_from_note(reportList):
    regexExtractEmail = r"[^\w.-]*([\w.-]+@([\w.-]+\.)+[a-z]{2,6})[^a-z]*"
    for eachRecord in reportList:
        eachRecord["Email"] = ""
        notes = eachRecord.get("Notes") or ""
        match = re.search(regexExtractEmail, notes)
        if match:
            eachRecord["Email"] = match[1]
    return reportList


def add_invoice_link(reportList):
    domain = os.environ.get("DOMAIN")
    for eachRecord in reportList:
        invoiceUrlBase = f"https://tech.{domain}/userinvoice/pdfinvoice.php?"
        invoiceNumber = str(eachRecord.get("InvoiceNumber") or "")
        loginName = eachRecord.get("LoginName") or ""
        cryptedLoginName = commons.simpleCrypt(loginName)
        cryptedInvoiceNumber = commons.simpleCrypt(invoiceNumber)
        queryString = urlencode(
            {"var1": cryptedLoginName, "var2": cryptedInvoiceNumber}
        )
        invoiceLink = f"{invoiceUrlBase}{queryString}"
        eachRecord["InvoiceLink"] = invoiceLink
    return reportList


def index(request):
    loginName = request.session.get("loginName")

    reportList = get_billing_list()
    report_list_with_info = extract_email_from_note(reportList)
    report_list_with_info = add_invoice_link(reportList)
    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "reportList": report_list_with_info,
    }
    return render(request, "latepayment/sample.html", context)
