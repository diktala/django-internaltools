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


class FormRestoreUser(forms.Form):
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
        required=True,
        min_length=1,
        max_length=250,
        validators=[
            RegexValidator(
                regex="^[\w. &'<>;+$()/=@,:*#\"\\[\]-]*$",
                message="invalid characters",
            )
        ],
    )
    CHOICES = [
        ("", "Select type"),
        ("0", "Regular restore"),
        ("1", "Override unpaid billing"),
    ]
    forceRestore = forms.ChoiceField(
        label="Force Restore",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
        choices=CHOICES,
        required=False,
    )


def get_user_info(loginName=""):
    querySQL = """EXECUTE InfoUser @LoginName = %(loginName)s"""
    paramSQL = {"loginName": str(loginName)}
    userInfo = queryDBall(querySQL, paramSQL)
    return userInfo


def set_user_restored(loginName, userRestore):
    querySQL = """
        EXECUTE RestoreUserSAM
        @LoginName = %(loginName)s
        ,@Operator = %(operator)s
        ,@Comments = %(specialNote)s
        ,@ForceRestore = %(forceRestore)s
    """
    paramSQL = {
        "loginName": loginName,
        "operator": userRestore.get("operator"),
        "specialNote": userRestore.get("specialNote"),
        "forceRestore": userRestore.get("forceRestore"),
    }
    print(f"DEBUG: querySQL: {querySQL}")
    print(f"DEBUG: paramSQL: {paramSQL}")
    # userInfo = queryDBall(querySQL, paramSQL)


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
    formRestoreUser = FormRestoreUser(initial=defaultData)
    #
    # pre assign parameters
    loginName = defaultData.get("loginName")
    userInfo = list([])
    if request.method == "POST" and request.POST.get("updateItemBTN"):
        formRestoreUser = FormRestoreUser(request.POST.dict())
        if formRestoreUser.is_valid():
            operator = formRestoreUser.cleaned_data.get("operator")
            loginName = formRestoreUser.cleaned_data.get("loginName")
            loginName = commons.get_loginname_from_database(loginName)
            if loginName:
                request.session["loginName"] = loginName
                request.session["operator"] = operator
                set_user_restored(loginName, formRestoreUser.cleaned_data)
                userInfo = get_user_info(loginName)
                messages.add_message(request, messages.SUCCESS, f"Form is VALID")
            else:
                messages.add_message(request, messages.WARNING, f"user is INVALID")
        else:
            messages.add_message(request, messages.WARNING, f"Form is INVALID")

    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formRestoreUser": formRestoreUser,
        "userInfo": userInfo[0] if len(userInfo) > 0 else None,
    }
    return render(request, "restoreuser/sample.html", context)
