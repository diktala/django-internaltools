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


class FormResolveIssue(forms.Form):
    transNum = forms.DecimalField(
        label="Transaction ID",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=True,
        max_digits=10,
        decimal_places=0,
    )
    resolveComment = forms.CharField(
        label="Resolve comment",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=1,
        max_length=20,
        validators=[
            RegexValidator(
                regex="^[\w. +$/=@,:*#-]*$",
                message="invalid characters",
            )
        ],
    )


def getOutstandingIssues():
    aladinSQL1 = """
        EXECUTE GetOutstandingTransactions
    """
    outstandingIssues = queryDBall(aladinSQL1)
    return outstandingIssues


def setOutstandingIssue(transNum="", resolveComment=""):
    aladinSQL1 = """
        EXECUTE GetOutstandingTransactions
            @TranNum = %(transNum)s
            , @Desc2 = %(resolveComment)s
    """
    aladinParam1 = {
        "transNum": transNum,
        "resolveComment": resolveComment,
    }
    queryDBall(aladinSQL1, aladinParam1)


def index(request):
    loginName = request.session.get("loginName")
    if request.method == "POST" and request.POST.get("updateItemBTN"):
        formResolveIssue = FormResolveIssue(request.POST.dict())
        if formResolveIssue.is_valid():
            transNum = formResolveIssue.cleaned_data.get("transNum")
            resolveComment = formResolveIssue.cleaned_data.get("resolveComment")
            setOutstandingIssue(transNum, resolveComment)
            messages.add_message(request, messages.SUCCESS, f"Resolved")
        else:
            messages.add_message(request, messages.WARNING, f"Form is INVALID")

    formResolveIssue = FormResolveIssue()
    outstandingIssues = getOutstandingIssues()
    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "outstandingIssues": outstandingIssues,
        "formResolveIssue": formResolveIssue,
    }
    return render(request, "outstandingissues/sample.html", context)
