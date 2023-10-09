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
    extendedSearch = forms.BooleanField(
        label="Include call logs?",
        initial="",
        widget=forms.CheckboxInput(
            attrs={
                "placeholder": "...",
                "class": "form-control form-check-input",
                "role": "switch",
            }
        ),
        required=False,
    )


def get_search_result(loginName="", extendedSearch=False):
    querySQL = """
        EXECUTE InfoUser2
            @HintName = %(loginName)s
            , @ExtendedSearch = %(extendedSearch)s
            """
    paramSQL = {
        "loginName": str(loginName),
        "extendedSearch": "1" if extendedSearch else "",
    }
    print(f"DEBUG: querySQL: {querySQL}")
    print(f"DEBUG: paramSQL: {paramSQL}")
    searchResult = queryDBall(querySQL, paramSQL)
    return searchResult


def index(request):
    # get loginname from POST or from URL
    defaultData = {
        "loginName": request.POST.get("loginName")
        or request.GET.get("loginName")
        or request.GET.get("LoginName")
        or request.session.get("loginName")
        or "",
        "extendedSearch": request.POST.get("extendedSearch"),
    }
    formSearchLogin = FormSearchLogin(defaultData)
    #
    # pre assign parameters
    loginName = defaultData.get("loginName")
    isUserExist = False
    userSearch = list([])
    # Check if valid login request received
    if formSearchLogin.is_valid():
        loginName = formSearchLogin.cleaned_data.get("loginName")
        extendedSearch = formSearchLogin.cleaned_data.get("extendedSearch")
        userSearch = get_search_result(loginName, extendedSearch)
        if len(userSearch) > 0:
            # found users
            isUserExist = True
    """ --- """
    #
    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "isDisabled": "" if isUserExist else "disabled",
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formSearchLogin": formSearchLogin,
        "userSearch": userSearch,
    }
    return render(request, "usersearch/sample.html", context)
