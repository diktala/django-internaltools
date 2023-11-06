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


class FormReactivateUser(forms.Form):
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
    OPERATORS = "Other " + commons.get_operators()
    operatorNames = OPERATORS or "Other"
    operator = forms.ChoiceField(
        choices=[(op, op) for op in operatorNames.split(" ")],
        initial="Other",
        label="operator",
        widget=forms.Select(
            attrs={
                "class": "form-control form-select",
            }
        ),
        required=False,
        validators=[
            RegexValidator(
                regex="^[\w. &'-]*[\w.]$",
                message="invalid characters",
            )
        ],
    )


def get_user_info(loginName=""):
    querySQL = """EXECUTE InfoUser @LoginName = %(loginName)s"""
    paramSQL = {"loginName": str(loginName)}
    userInfo = queryDBall(querySQL, paramSQL)
    return userInfo


def set_user_active(loginName, operator):
    querySQL = """
        EXECUTE ActivateUserSAM
        @LoginName = %(loginName)s
        ,@Operator = %(operator)s
        ,@DebugLevel = %(debugLevel)d
    """
    paramSQL = {
        "loginName": loginName,
        "operator": operator,
        "debugLevel": 1,
    }
    print(f"DEBUG: querySQL: {querySQL}")
    print(f"DEBUG: paramSQL: {paramSQL}")
    result = queryDBall(querySQL, paramSQL)
    return result


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
    formReactivateUser = FormReactivateUser(initial=defaultData)
    #
    # pre assign parameters
    loginName = defaultData.get("loginName")
    userInfo = list()
    freezeForm = False
    if request.method == "POST" and request.POST.get("updateItemBTN"):
        formReactivateUser = FormReactivateUser(request.POST.dict())
        if formReactivateUser.is_valid():
            operator = formReactivateUser.cleaned_data.get("operator")
            loginName = formReactivateUser.cleaned_data.get("loginName")
            loginName = commons.get_loginname_from_database(loginName)
            if loginName:
                request.session["loginName"] = loginName
                request.session["operator"] = operator
                result = set_user_active(loginName, operator)
                userInfo = get_user_info(loginName)
                freezeForm = True
                try:
                    resultMsg = result[0].get("ResultInfo", "")
                except:
                    resultMsg = ""
                messages.add_message(request, messages.SUCCESS, f"Result: {resultMsg}")
            else:
                messages.add_message(request, messages.WARNING, f"user is INVALID")
        else:
            messages.add_message(request, messages.WARNING, f"Form is INVALID")

    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "freezeForm": freezeForm,
        "formReactivateUser": formReactivateUser,
        "userInfo": userInfo[0] if len(userInfo) > 0 else None,
    }
    return render(request, "reactivateuser/sample.html", context)
