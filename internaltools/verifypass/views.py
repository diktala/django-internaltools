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


class FormVerifyPassword(forms.Form):
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
    verifyPassword = forms.CharField(
        label="Verify Password",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=1,
        max_length=20,
        validators=[
            RegexValidator(
                # regex="^[\w. +$()/=@,:*#-]*$",
                regex="""^[\w. &'<>;+$()/=@,:*#"\[\]-]*$""",
                message="invalid characters",
            )
        ],
    )


def get_password_hint(userDict):
    loginName = userDict.get("loginName")
    verifyPassword = userDict.get("verifyPassword")
    querySQL = """
        EXECUTE VerifyPassword
        @LoginName = %(loginName)s
        ,@VerifyPassword = %(verifyPassword)s
    """
    paramSQL = {
        "loginName": userDict.get("loginName"),
        "verifyPassword": userDict.get("verifyPassword"),
    }
    # print(f"DEBUG: querySQL: {querySQL}")
    # print(f"DEBUG: paramSQL: {paramSQL}")
    passwordHint = queryDBall(querySQL, paramSQL)
    return passwordHint


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
    formVerifyPassword = FormVerifyPassword(initial=defaultData)
    #
    # pre assign parameters
    loginName = defaultData.get("loginName")
    passwordHint = list()
    if request.method == "POST" and request.POST.get("updateItemBTN"):
        formVerifyPassword = FormVerifyPassword(request.POST.dict())
        if formVerifyPassword.is_valid():
            loginName = formVerifyPassword.cleaned_data.get("loginName")
            if is_login_exist(loginName):
                request.session["loginName"] = loginName
                passwordHint = get_password_hint(formVerifyPassword.cleaned_data)
            else:
                messages.add_message(request, messages.WARNING, f"user was not found")

    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formVerifyPassword": formVerifyPassword,
        "passwordHint": passwordHint[0] if len(passwordHint) > 0 else None,
    }
    return render(request, "verifypass/sample.html", context)
