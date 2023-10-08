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
import commons


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


class FormCallLog(forms.Form):
    loginName = forms.CharField(
        widget=forms.HiddenInput(
            attrs={
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
                "placeholder": "... type call log ...",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=1,
        max_length=200,
        validators=[
            RegexValidator(
                # regex="^[\w. &'<>;+$()/=@,:*#\"\\[\]-]*$",
                regex="^[\w. +$()/=@,:*#-]*$",
                message="invalid characters",
            )
        ],
    )
    requiresFeedback = forms.BooleanField(
        label="Feedback?",
        initial="",
        widget=forms.CheckboxInput(
            attrs={
                "placeholder": "...",
                "class": "form-control form-check-input",
            }
        ),
        required=False,
    )


def get_user_info(loginName=""):
    querySQL = """EXECUTE InfoUser @LoginName = %(loginName)s"""
    paramSQL = {"loginName": str(loginName)}
    userInfo = queryDBall(querySQL, paramSQL)
    return userInfo


def get_user_plans(loginName=""):
    querySQL = """EXECUTE UpdateUsersPlans @LoginName = %(loginName)s"""
    paramSQL = {"loginName": str(loginName)}
    planDict = queryDBall(querySQL, paramSQL)
    return planDict


def get_call_logs(loginName=""):
    querySQL = """
        EXECUTE GetUserProfile
            @LoginName = %(loginName)s
            , @Operator = %(operator)s
            , @Desc1 = %(specialNote)s
            , @ReqAttention = %(requiresFeedback)s
            """
    paramSQL = {
        "loginName": str(loginName),
        "operator": "",
        "specialNote": "",
        "requiresFeedback": "",
    }
    callLogDict = queryDBall(querySQL, paramSQL)
    return callLogDict


def submitToAladin(callLogDict):
    updateAladinSQL1 = f"""
        EXECUTE GetUserProfile
            @LoginName = %(loginName)s
            , @Operator = %(operator)s
            , @Desc1 = %(specialNote)s
            , @ReqAttention = %(requiresFeedback)s
            """
    updateAladinParam1 = {
        "loginName": str(callLogDict.get("loginName")),
        "operator": str(callLogDict.get("operator")),
        "specialNote": str(callLogDict.get("specialNote")),
        "requiresFeedback": "1" if callLogDict.get("requiresFeedback") else "",
    }
    # print(f"DEBUG MESSAGE: {updateAladinSQL1}")
    # print(f"DEBUG MESSAGE: {updateAladinParam1}")
    queryDBall(updateAladinSQL1, updateAladinParam1)


def index(request):
    # get loginname from POST or from URL
    defaultData = {
        "loginName": request.POST.get("loginName")
        or request.GET.get("loginName")
        or request.GET.get("LoginName")
        or request.session.get('loginName')
        or "",
    }
    formSearchLogin = FormSearchLogin(defaultData)
    formCallLog = FormCallLog()
    #
    # pre assign parameters
    loginName = defaultData.get("loginName")
    isUserExist = False
    userInfo = list([])
    userPlans = list([])
    callLogs = list([])
    # Check if valid login request received
    if formSearchLogin.is_valid():
        loginName = formSearchLogin.cleaned_data.get("loginName")
        confirmedLoginName = commons.get_loginname_from_database(loginName)
        userInfo = get_user_info(confirmedLoginName)
        userPlans = get_user_plans(confirmedLoginName)
        callLogs = get_call_logs(confirmedLoginName)
        if userInfo:
            # found user info for this user
            isUserExist = True
            formCallLog.fields["loginName"].initial = confirmedLoginName
            formCallLog.fields["operator"].initial = request.session.get("operator")
            # store in cookie session
            request.session['loginName'] = confirmedLoginName
    """ --- """
    # item button was submitted
    if request.method == "POST" and request.POST.get("updateItemBTN"):
        formCallLog = FormCallLog(request.POST.dict())
        if formCallLog.is_valid():
            submit_invoice_to_aladin = formCallLog.cleaned_data
            # print(f"DEBUG MESSAGE: {formCallLog.cleaned_data}")
            submitToAladin(submit_invoice_to_aladin)
            messages.add_message(request, messages.SUCCESS, f"form is VALID")
            # save operator in cookie session
            request.session['operator'] = formCallLog.cleaned_data.get("operator")
            # refresh the callLogs to show the new entry
            loginName = formCallLog.cleaned_data.get("loginName")
            callLogs = get_call_logs(loginName)
            # clear the callLog form
            formCallLog = FormCallLog()
            formCallLog.fields["loginName"].initial = loginName
            formCallLog.fields["operator"].initial = request.session.get('operator')
        else:
            messages.add_message(request, messages.WARNING, f"form is still INVALID")
            # messages.add_message(request, messages.INFO, f"error is:  {form_being_updated.errors}")
    #
    urlQuery = f"LoginName={loginName}"
    context = {
        # "debugMessage": debugMessage,
        "loginName": loginName,
        "isDisabled": "" if isUserExist else "disabled",
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formSearchLogin": formSearchLogin,
        "formCallLog": formCallLog,
        "userInfo": userInfo[0] if len(userInfo) > 0 else None,
        "userPlans": userPlans,
        "callLogs": callLogs,
    }
    return render(request, "infouser/sample.html", context)
