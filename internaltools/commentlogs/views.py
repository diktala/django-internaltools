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


class FormListComments(forms.Form):
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
        ("Operator", "Sort by Operator"),
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


def get_summary_logs(listUsers):
    try:
        daysAgo = int(listUsers.get("daysAgo", 14))
    except ValueError:
        pass
    if not isinstance(daysAgo, int):
        daysAgo = 14
    sortIndex = (
        "TranDate"
        if (listUsers.get("sortIndex", "TranDate") == "TranDate")
        else "Operator"
    )

    querySQL = """
        SELECT TransactionHistory.Operator
            , Count(TransactionHistory.Operator) AS 'CountOfOperator'
            FROM TransactionHistory
            WHERE (TransactionHistory.TranDate>getdate()- %(daysAgo)d )
                AND (TransactionHistory.Type='CallLog')
            GROUP BY TransactionHistory.Operator
            HAVING Count(Operator) > 10
            ;
        """
    paramSQL = {
        "daysAgo": int(daysAgo),
    }
    # print(f"DEBUG: querySQL: {querySQL}")
    # print(f"DEBUG: paramSQL: {paramSQL}")
    summaryLogs = queryDBall(querySQL, paramSQL)
    return summaryLogs


def get_comment_logs(listUsers):
    try:
        daysAgo = int(listUsers.get("daysAgo", 14))
    except ValueError:
        pass
    if not isinstance(daysAgo, int):
        daysAgo = 14
    sortIndex = (
        "TranDate"
        if (listUsers.get("sortIndex", "TranDate") == "TranDate")
        else "Operator"
    )

    querySQL = f"""
        SELECT TransactionHistory.TranNum
            , TransactionHistory.TranDate
            , TransactionHistory.LoginName
            , TransactionHistory.Operator
            , TransactionHistory.Desc1
            , TransactionHistory.Desc2
            , TransactionHistory.ReqAttention
            FROM TransactionHistory
            WHERE (TransactionHistory.TranDate>getdate() - %(daysAgo)d )
                AND (TransactionHistory.Type='CallLog')
            ORDER BY {sortIndex} DESC
        ;
        """
    paramSQL = {
        "daysAgo": int(daysAgo),
        "sortIndex": sortIndex,
    }
    # print(f"DEBUG: querySQL: {querySQL}")
    # print(f"DEBUG: paramSQL: {paramSQL}")
    commentLogs = queryDBall(querySQL, paramSQL)
    return commentLogs


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
    formListComments = FormListComments(initial=defaultData)
    #
    # pre assign parameters
    loginName = defaultData.get("loginName")
    userComments = list([])
    summaryComments = list([])

    if request.method == "POST" and (request.POST.get("updateItemBTN")):
        formListComments = FormListComments(request.POST.dict())
        if formListComments.is_valid():
            summaryComments = get_summary_logs(formListComments.cleaned_data)
            userComments = get_comment_logs(formListComments.cleaned_data)

    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formListComments": formListComments,
        "userComments": userComments,
        "summaryComments": summaryComments,
    }
    return render(request, "commentlogs/sample.html", context)
