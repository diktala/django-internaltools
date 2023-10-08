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


class FormMailAccount(forms.Form):
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
                "placeholder": "[enter note ...]",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=1,
        max_length=250,
        validators=[
            RegexValidator(
                # regex="^[\w. &'<>;+$()/=@,:*#\"\\[\]-]*$",
                regex="^[\w. +$()/=@,:*#-]*$",
                message="invalid characters",
            )
        ],
    )
    setForDelete = forms.BooleanField(
        label="Delete?",
        initial="",
        widget=forms.CheckboxInput(
            attrs={
                "placeholder": "...",
                "class": "form-control form-check-input",
            }
        ),
        required=False,
    )
    mailAccount = forms.CharField(
        label="Email Account",
        widget=forms.TextInput(
            attrs={
                "placeholder": "[new mail ...]",
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
    mailPassword = forms.CharField(
        label="Email Password",
        widget=forms.TextInput(
            attrs={
                "placeholder": "[mail password ...]",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=1,
        max_length=20,
        validators=[
            RegexValidator(
                regex="^[a-z0-9][a-z0-9.-]*[a-z0-9]$",
                message="invalid characters",
            )
        ],
    )

    def clean(self):
        cleaned_data = super().clean()
        mailAccount = cleaned_data.get("mailAccount")
        mailPassword = cleaned_data.get("mailPassword")
        setForDelete = cleaned_data.get("setForDelete")
        """ --- """
        if (
            mailAccount is not None
            and mailPassword is not None
            and setForDelete is not None
        ):
            if not setForDelete and len(mailPassword) == 0:
                self.add_error("mailPassword", "password missing")
        return self.cleaned_data


def get_mail_accounts(loginName=""):
    querySQL = """
        EXECUTE SecondaryMailAccount
            @LoginName = %(loginName)s
            , @Operator = %(operator)s
            , @SecondaryAccount = %(mailAccount)s
            , @SecondaryPassword = %(mailPassword)s
            , @Comments = %(specialNote)s
            , @SetForDelete = %(setForDelete)s
            """
    paramSQL = {
        "loginName": str(loginName),
        "operator": "",
        "mailAccount": "",
        "mailPassword": "",
        "specialNote": "",
        "setForDelete": "",
    }
    mailDict = queryDBall(querySQL, paramSQL)
    return mailDict


def submitToAladin(mailAccountDict):
    updateAladinSQL1 = f"""
        EXECUTE SecondaryMailAccount
            @LoginName = %(loginName)s
            , @Operator = %(operator)s
            , @SecondaryAccount = %(mailAccount)s
            , @SecondaryPassword = %(mailPassword)s
            , @Comments = %(specialNote)s
            , @SetForDelete = %(setForDelete)s
            """
    updateAladinParam1 = {
        "loginName": str(mailAccountDict.get("loginName")),
        "operator": str(mailAccountDict.get("operator")),
        "mailAccount": str(mailAccountDict.get("mailAccount")),
        "mailPassword": str(mailAccountDict.get("mailPassword")),
        "specialNote": str(mailAccountDict.get("specialNote")),
        "setForDelete": "1" if mailAccountDict.get("setForDelete") else "",
    }
    print(f"DEBUG MESSAGE: {updateAladinSQL1}")
    print(f"DEBUG MESSAGE: {updateAladinParam1}")
    # queryDBall(updateAladinSQL1, updateAladinParam1)


def create_forms_from_items(mailAccounts, defaultOperator=""):
    dict_of_forms = dict()
    defaultLoginName = ""
    if len(mailAccounts) > 1:
        defaultLoginName = mailAccounts[0].get("LoginName")
    for eachMailAccount in mailAccounts:
        formMailAccount = FormMailAccount()
        formMailAccount.fields["loginName"].initial = eachMailAccount.get("LoginName")
        formMailAccount.fields["operator"].initial = defaultOperator
        formMailAccount.fields["mailAccount"].initial = eachMailAccount.get(
            "SecondaryAccount"
        )
        formMailAccount.fields["mailAccount"].widget.attrs["readonly"] = "readonly"
        mailAccount = eachMailAccount.get("SecondaryAccount")
        dict_of_forms[mailAccount] = formMailAccount
    return dict_of_forms


def index(request):
    # get loginname from POST or from URL
    defaultData = {
        "loginName": request.POST.get("loginName")
        or request.GET.get("loginName")
        or request.GET.get("LoginName")
        or request.session.get("loginName")
        or "",
    }
    formSearchLogin = FormSearchLogin(defaultData)
    # pre assign parameters
    loginName = defaultData.get("loginName")
    isUserExist = False
    # dict_of_forms: a form for each mail account
    dict_of_forms = dict()
    emptyFormMailAccount = dict()
    mailAccounts = list([])
    # Check if valid login request received
    if formSearchLogin.is_valid():
        loginName = formSearchLogin.cleaned_data.get("loginName")
        confirmedLoginName = commons.get_loginname_from_database(loginName)
        if confirmedLoginName:
            isUserExist = True
            # store loginName in cookie session
            request.session["loginName"] = confirmedLoginName
            defaultOperator = request.session.get("operator")
            # generate empty mailAccount form for new account
            emptyFormMailAccount = FormMailAccount()
            emptyFormMailAccount.fields["loginName"].initial = confirmedLoginName
            emptyFormMailAccount.fields["operator"].initial = defaultOperator
            # generate existing mailAccount forms
            mailAccounts = get_mail_accounts(confirmedLoginName)
            dict_of_forms = create_forms_from_items(mailAccounts, defaultOperator)
    """ --- """
    # item button was submitted
    if request.method == "POST" and (
        request.POST.get("updateItemBTN") or request.POST.get("addItemBTN")
    ):
        formMailAccount = FormMailAccount(request.POST.dict())
        if formMailAccount.is_valid():
            # print(f"DEBUG MESSAGE: {formMailAccount.cleaned_data}")
            submit_invoice_to_aladin = formMailAccount.cleaned_data
            submitToAladin(submit_invoice_to_aladin)
            messages.add_message(request, messages.SUCCESS, f"form is VALID")
            # save operator in cookie session
            operator = formMailAccount.cleaned_data.get("operator")
            request.session["operator"] = operator
            # refresh the list of forms
            mailAccounts = get_mail_accounts(loginName)
            dict_of_forms = create_forms_from_items(mailAccounts, operator)
        else:
            messages.add_message(request, messages.WARNING, f"form is still INVALID")
            if request.POST.get("updateItemBTN"):
                # add POSTed info to the existing mail form
                form_updated = request.POST.get("mailAccount")
                dict_of_forms[form_updated] = formMailAccount
            else:
                # add POSTed info to the create new mail form
                emptyFormMailAccount = FormMailAccount(request.POST.dict())
    #
    urlQuery = f"LoginName={loginName}"
    context = {
        # "debugMessage": debugMessage,
        "loginName": loginName,
        "isDisabled": "" if isUserExist else "disabled",
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formSearchLogin": formSearchLogin,
        "dict_of_forms": dict_of_forms,
        "emptyFormMailAccount": emptyFormMailAccount,
    }
    return render(request, "mailaccount/sample.html", context)
