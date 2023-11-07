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


class FormListUsers(forms.Form):
    daysAgo = forms.DecimalField(
        label="Days from now",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
        initial=14,
        required=True,
        max_digits=2,
        decimal_places=0,
    )
    CHOICES = [
        ("TranDate", "Sort by Date"),
        ("LoginName", "Sort by Login"),
    ]
    sortIndex = forms.ChoiceField(
        label="Sort Index",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
        choices=CHOICES,
        required=True,
    )


class FormAcknowledgeAccess(forms.Form):
    transactionNumber = forms.DecimalField(
        label="Transaction Number",
        widget=forms.HiddenInput(
            attrs={
                "class": "form-control",
            }
        ),
        required=True,
        max_digits=10,
        decimal_places=0,
    )
    specialNote = forms.CharField(
        label="Special Note",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=1,
        max_length=250,
        validators=[
            RegexValidator(
                regex="^[\w. <>+$/=@,:*#-]*$",
                message="invalid characters",
            )
        ],
    )


def get_user_input(listUsers):
    try:
        daysAgo = int(listUsers.get("daysAgo", 14))
    except ValueError:
        pass
    if not isinstance(daysAgo, int):
        daysAgo = 14
    sortIndex = (
        "TranDate"
        if (listUsers.get("sortIndex", "TranDate") == "TranDate")
        else "LoginName"
    )

    querySQL = """
        SET rowcount 500; 
        SELECT TransactionHistory.TranNum
            , TransactionHistory.TranDate
            , TransactionHistory.LoginName
            , TransactionHistory.Operator
            , TransactionHistory.Desc1
            , TransactionHistory.Desc2
            , TransactionHistory.ReqAttention
            FROM TransactionHistory
            WHERE TransactionHistory.TranDate>getdate() - %(daysAgo)d
                AND (TransactionHistory.TranID between 11410 and 11419) 
                AND TransactionHistory.Desc2 is null 
                AND TransactionHistory.Operator = 'AuthenticatedUser'
            ORDER BY %(sortIndex)s 
            ;
        SET rowcount 0;
        """
    paramSQL = {
        "daysAgo": int(daysAgo),
        "sortIndex": sortIndex,
    }
    # print(f"DEBUG: querySQL: {querySQL}")
    # print(f"DEBUG: paramSQL: {paramSQL}")
    userInput = queryDBall(querySQL, paramSQL)
    return userInput


def acknowledge_user_access(acknowledge):
    specialNote = ""
    transactionNumber = 0
    try:
        specialNote = str(acknowledge.get("specialNote"))
        transactionNumber = int(acknowledge.get("transactionNumber"))
    except ValueError:
        pass
    querySQL = """
        UPDATE TransactionHistory
        SET Desc2 = isnull(Desc2, '') + %(specialNote)s
        WHERE TranNum = %(transactionNumber)d
        """
    paramSQL = {
        "specialNote": specialNote,
        "transactionNumber": transactionNumber,
    }
    queryDBall(querySQL, paramSQL)


def index(request):
    # get loginname from POST or from URL
    defaultData = {
        "loginName": request.POST.get("loginName")
        or request.GET.get("loginName")
        or request.GET.get("LoginName")
        or request.session.get("loginName")
        or "",
        "operator": request.POST.get("operator") or request.session.get("operator"),
    }
    formListUsers = FormListUsers(initial=defaultData)
    formAcknowledgeAccess = FormAcknowledgeAccess()
    #
    # pre assign parameters
    loginName = defaultData.get("loginName")
    userInput = list()
    if request.method == "POST" and request.POST.get("resetAccessBTN"):
        formAcknowledgeAccess = FormAcknowledgeAccess(request.POST.dict())
        if formAcknowledgeAccess.is_valid():
            messages.add_message(request, messages.SUCCESS, f"ACK received")
            resetAccess = acknowledge_user_access(formAcknowledgeAccess.cleaned_data)

    if request.method == "POST" and (
        request.POST.get("updateItemBTN") or request.POST.get("resetAccessBTN")
    ):
        formListUsers = FormListUsers(request.POST.dict())
        if formListUsers.is_valid():
            userInput = get_user_input(formListUsers.cleaned_data)

    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formListUsers": formListUsers,
        "userInput": userInput,
        "formAcknowledgeAccess": formAcknowledgeAccess,
    }
    return render(request, "userinput/sample.html", context)
