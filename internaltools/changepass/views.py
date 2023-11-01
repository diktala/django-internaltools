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


class FormChangePassword(forms.Form):
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
    specialNote = forms.CharField(
        label="Special Note",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=1,
        max_length=250,
        validators=[
            RegexValidator(
                regex="^[\w. &'<>;+$()/=@,:*#\"\\[\]-]*$",
                message="invalid characters",
            )
        ],
    )
    newPassword = forms.CharField(
        label="New Password",
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
                regex="^[A-Za-z0-9!@#$%^&*=+._-]+$",
                message="invalid characters",
            )
        ],
    )


def get_user_info(loginName=""):
    querySQL = """EXECUTE InfoUser @LoginName = %(loginName)s"""
    paramSQL = {"loginName": str(loginName)}
    userInfo = queryDBall(querySQL, paramSQL)
    return userInfo


def set_user_password(loginName, userPassword):
    querySQL = """
        EXECUTE ForceChangeNTPassword
        @LoginName = %(loginName)s
        ,@Operator = %(operator)s
        ,@Comments = %(specialNote)s
        ,@NewPassword = %(newPassword)s
        ,@DebugLevel = %(debugLevel)s
    """
    paramSQL = {
        "loginName": loginName,
        "operator": userPassword.get("operator"),
        "specialNote": userPassword.get("specialNote"),
        "newPassword": userPassword.get("newPassword"),
        "debugLevel": 1,
    }
    # print(f"DEBUG: querySQL: {querySQL}")
    # print(f"DEBUG: paramSQL: {paramSQL}")
    userInfo = queryDBall(querySQL, paramSQL)


def is_login_exist(loginName):
    isLoginExist = False
    if commons.count_loginnames_in_database(
        loginName
    ) or commons.get_loginname_from_secondary_mail(loginName):
        isLoginExist = True
    return isLoginExist


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
    formChangePassword = FormChangePassword(initial=defaultData)
    #
    # pre assign parameters
    loginName = defaultData.get("loginName")
    userInfo = list([])
    if request.method == "POST" and request.POST.get("updateItemBTN"):
        formChangePassword = FormChangePassword(request.POST.dict())
        if formChangePassword.is_valid():
            operator = formChangePassword.cleaned_data.get("operator")
            loginName = formChangePassword.cleaned_data.get("loginName")
            isLoginExist = is_login_exist(loginName)
            if isLoginExist:
                request.session["loginName"] = loginName
                request.session["operator"] = operator
                set_user_password(loginName, formChangePassword.cleaned_data)
                userInfo = get_user_info(loginName)
                messages.add_message(request, messages.SUCCESS, f"Password updated")
            else:
                messages.add_message(request, messages.WARNING, f"user was not found")

    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formChangePassword": formChangePassword,
        "userInfo": userInfo[0] if len(userInfo) > 0 else None,
    }
    return render(request, "changepass/sample.html", context)
