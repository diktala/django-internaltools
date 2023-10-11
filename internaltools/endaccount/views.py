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


class FormEndAccount(forms.Form):
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
    OPERATORS = os.environ.get("OPERATORS")
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
        ("", "Enter Date"),
        ("0", "Join Date"),
        ("1", "Immediate"),
        ("2", "End of month"),
    ]
    terminationType = forms.ChoiceField(
        label="Termination Type",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
        choices=CHOICES,
        required=False,
    )
    specifyDate = forms.CharField(
        label="Termination Date",
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
                regex="^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
                message="format 0000-00-00",
            )
        ],
    )

    def clean(self):
        cleaned_data = super().clean()
        specifyDate = cleaned_data.get("specifyDate")
        """ --- """
        if specifyDate is not None and len(specifyDate) > 0:
            if not commons.isDateValid(specifyDate):
                self.add_error("specifyDate", "invalid date")
        return self.cleaned_data


def get_user_info(loginName=""):
    querySQL = """EXECUTE InfoUser @LoginName = %(loginName)s"""
    paramSQL = {"loginName": str(loginName)}
    userInfo = queryDBall(querySQL, paramSQL)
    return userInfo


def set_user_terminated(loginName, userTerminate):
    querySQL = """
        EXECUTE TerminateUser
        @LoginName = %(loginName)s,
        @Operator = %(operator)s,
        @Comments = %(specialNote)s,
        @ForceDisable = %(terminationType)s,
        @TerminateDate = %(specifyDate)s
    """
    paramSQL = {
        "loginName": loginName,
        "operator": userTerminate.get("operator"),
        "specialNote": userTerminate.get("specialNote"),
        "terminationType": userTerminate.get("terminationType"),
        "specifyDate": userTerminate.get("specifyDate"),
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
    formEndAccount = FormEndAccount(initial=defaultData)
    #
    # pre assign parameters
    loginName = defaultData.get("loginName")
    userInfo = list([])
    if request.method == "POST" and request.POST.get("updateItemBTN"):
        formEndAccount = FormEndAccount(request.POST.dict())
        if formEndAccount.is_valid():
            operator = formEndAccount.cleaned_data.get("operator")
            loginName = formEndAccount.cleaned_data.get("loginName")
            loginName = commons.get_loginname_from_database(loginName)
            if loginName:
                request.session["loginName"] = loginName
                request.session["operator"] = operator
                set_user_terminated(loginName, formEndAccount.cleaned_data)
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
        "formEndAccount": formEndAccount,
        "userInfo": userInfo[0] if len(userInfo) > 0 else None,
    }
    return render(request, "endaccount/sample.html", context)
