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
from fabric import Connection
import json


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


class FormDomain(forms.Form):
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
    domainSelect = forms.ChoiceField(
        choices=[("", "Select domain")],
        initial="",
        label="Select domain",
        widget=forms.Select(
            attrs={
                "class": "form-control form-select",
            }
        ),
        required=False,
    )
    newDomain = forms.CharField(
        label="Add domain",
        widget=forms.TextInput(
            attrs={
                "placeholder": "[... ex: example.com]",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=1,
        max_length=250,
        validators=[
            RegexValidator(
                regex="^[a-z0-9][0-9a-z.-]+[.][a-z]{2,}$",
                message="should be similar to: example.com",
            )
        ],
    )
    confirmDelete = forms.CharField(
        label="Confirm Delete",
        initial="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "[... ex: example.com]",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=1,
        max_length=250,
        validators=[
            RegexValidator(
                regex="^[0-9a-z.-]+$",
                message="invalid characters",
            )
        ],
    )
    originalSourceEmail = forms.CharField(
        label="Original Source Email",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=3,
        max_length=50,
        validators=[
            RegexValidator(
                regex="^[a-z0-9._-]+$",
                message="invalid characters",
            )
        ],
    )
    sourceEmail = forms.CharField(
        label="Source Email",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=3,
        max_length=50,
        validators=[
            RegexValidator(
                regex="^[a-z0-9._-]+$",
                message="invalid characters",
            )
        ],
    )
    originalDestinationEmail = forms.CharField(
        label="Original Destination Email",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=3,
        max_length=50,
        validators=[
            RegexValidator(
                regex="^[%@a-z0-9._-]+$",
                message="invalid characters",
            )
        ],
    )
    destinationEmail = forms.CharField(
        label="Destination Email",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=3,
        max_length=50,
        validators=[
            RegexValidator(
                regex="^[%@a-z0-9._-]+$",
                message="invalid characters",
            )
        ],
    )


def update_alias_in_webhosting(
    originalSourceEmail="",
    domainName="",
    originalDestinationEmail="",
    newSourceEmail="",
    newDestinationEmail="",
):
    webhosting_host = os.environ.get("WEBHOSTING_HOST", "")
    webhosting_user = os.environ.get("WEBHOSTING_USER", "")
    listDomains = "./webhosting_virtusertable_update.sh "
    listDomains += f" '{originalSourceEmail}' "
    listDomains += f" '{domainName}' "
    listDomains += f" '{originalDestinationEmail}' "
    listDomains += f" '{newSourceEmail}' "
    listDomains += f" '{newDestinationEmail}' "
    result = Connection(webhosting_host, user=webhosting_user, connect_timeout=1).sudo(
        listDomains, hide=True, warn=True
    )
    output = list()
    if isinstance(result.stdout, str):
        output = result.stdout.splitlines()
    return output


def remove_alias_from_webhosting(sourceEmail="", domainName="", destinationEmail=""):
    webhosting_host = os.environ.get("WEBHOSTING_HOST", "")
    webhosting_user = os.environ.get("WEBHOSTING_USER", "")
    listDomains = "./webhosting_virtusertable_remove.sh "
    listDomains += f" '{sourceEmail}' '{domainName}' '{destinationEmail}'"
    result = Connection(webhosting_host, user=webhosting_user, connect_timeout=1).sudo(
        listDomains, hide=True, warn=True
    )
    output = list()
    if isinstance(result.stdout, str):
        output = result.stdout.splitlines()
    return output


def add_alias_to_webhosting(sourceEmail="", domainName="", destinationEmail=""):
    webhosting_host = os.environ.get("WEBHOSTING_HOST", "")
    webhosting_user = os.environ.get("WEBHOSTING_USER", "")
    listDomains = "./webhosting_virtusertable_add.sh "
    listDomains += f" '{sourceEmail}' '{domainName}' '{destinationEmail}'"
    result = Connection(webhosting_host, user=webhosting_user, connect_timeout=1).sudo(
        listDomains, hide=True, warn=True
    )
    output = list()
    if isinstance(result.stdout, str):
        output = result.stdout.splitlines()
    return output


def get_domains_from_webhosting(loginName=""):
    webhosting_host = os.environ.get("WEBHOSTING_HOST", "")
    webhosting_user = os.environ.get("WEBHOSTING_USER", "")
    listDomains = "cat /usr/local/etc/namedb/named.conf "
    listDomains += f" | grep -E -A 3 'Start_section_{loginName}( |$)'"
    listDomains += " | grep -E '^ *zone '"
    listDomains += """  | sed -r 's=^[^"]+"([^"]+)".*=\\1=' """
    result = Connection(webhosting_host, user=webhosting_user, connect_timeout=1).run(
        listDomains, hide=True, warn=True
    )
    output = list()
    if isinstance(result.stdout, str):
        output = result.stdout.splitlines()
    return output


def get_alias_from_webhosting(domainName=""):
    webhosting_host = os.environ.get("WEBHOSTING_HOST", "")
    webhosting_user = os.environ.get("WEBHOSTING_USER", "")
    listVirtusertable = "cat /etc/mail/virtusertable "
    listVirtusertable += " | tr '\\t' ' ' "
    listVirtusertable += f" | grep -E '^[^@]*@{domainName} '"
    listVirtusertable += " | tr '\\t' ' ' | tr -s ' ' | tr ' ' ':' "
    listVirtusertable += """ | sed -r 's=^="=; s=:=":"=; s=$="=' """
    listVirtusertable += " | tr '\\n' ',' "
    listVirtusertable += " | sed -r 's=^={=; s=,$=}=' "
    result = Connection(webhosting_host, user=webhosting_user, connect_timeout=1).run(
        listVirtusertable, hide=True, warn=True
    )
    try:
        output = json.loads(result.stdout)
    except json.decoder.JSONDecodeError:
        output = dict()
    return output


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
    confirmedLoginName = None
    isUserExist = False
    formDomain = dict()
    formDomainWithoutEmails = dict()
    formEmailList = list(dict())
    defaultOperator = request.session.get("operator")
    # Check if valid login request received
    if formSearchLogin.is_valid():
        loginName = formSearchLogin.cleaned_data.get("loginName")
        confirmedLoginName = commons.get_loginname_from_database(loginName)
        if confirmedLoginName:
            isUserExist = True
            # store loginName in cookie session
            request.session["loginName"] = confirmedLoginName
            # get list of domains belonging to user
            domainList = get_domains_from_webhosting(confirmedLoginName)
            domainChoices = [(op, op) for op in domainList]
            # generate form
            defaultData = {
                "loginName": confirmedLoginName,
                "operator": defaultOperator,
            }
            # formDomainWithoutEmails: used for general form without emails.
            # this allows to have a valid form even if email alias is invalid
            formDomainWithoutEmails = FormDomain(
                defaultData
                | request.POST.dict()
                | {"sourceEmail": "", "destinationEmail": ""}
            )
            formDomainWithoutEmails.fields["domainSelect"].choices = domainChoices
            formDomain = FormDomain(defaultData | request.POST.dict())
            formDomain.fields["domainSelect"].choices = domainChoices

    # domain add
    if (
        request.method == "POST"
        and confirmedLoginName
        and request.POST.get("addDomainBTN")
        and request.POST.get("newDomain")
        and formDomainWithoutEmails.is_valid()
    ):
        messages.add_message(
            request,
            messages.WARNING,
            f"add domain is disabled. please contact administrator",
        )

    # domain delete
    if (
        request.method == "POST"
        and confirmedLoginName
        and request.POST.get("deleteBTN")
        and request.POST.get("confirmDelete")
        and request.POST.get("domainSelect")
        and request.POST.get("confirmDelete") == request.POST.get("domainSelect")
        and formDomainWithoutEmails.is_valid()
    ):
        messages.add_message(
            request,
            messages.WARNING,
            f"delete domain is disabled. please contact administrator",
        )

    # sync password
    if (
        request.method == "POST"
        and confirmedLoginName
        and request.POST.get("syncPasswordBTN")
        and formDomainWithoutEmails.is_valid()
    ):
        messages.add_message(
            request,
            messages.WARNING,
            f"sync password is disabled. please contact administrator",
        )

    # list emails
    if (
        request.method == "POST"
        and confirmedLoginName
        and request.POST.get("domainSelect")
    ):
        # create one form per email
        domainSelected = request.POST.get("domainSelect")
        aliasDict = get_alias_from_webhosting(domainSelected)
        # adding " " for new email alias
        aliasDict[" "] = ""
        formValuesPosted = request.POST.dict()
        for key, value in aliasDict.items():
            formValues = dict()
            formValues["domainSelect"] = domainSelected
            formValues["loginName"] = confirmedLoginName
            formValues["operator"] = defaultOperator
            formValues["originalSourceEmail"] = key.split("@")[0]
            formValues["originalDestinationEmail"] = value
            formValues["sourceEmail"] = key.split("@")[0]
            formValues["destinationEmail"] = value
            # find the correct form
            if formValuesPosted.get("originalSourceEmail") == key.split("@")[0]:
                formValues = formValues | request.POST.dict()
            formEmailList.append(FormDomain(formValues))
            lastForm = formEmailList[-1:][0]
            lastForm.fields["domainSelect"].choices = domainChoices
    # email update or delete
    if (
        request.method == "POST"
        and confirmedLoginName
        and request.POST.get("domainSelect")
        and formDomain.is_valid()
        and (
            request.POST.get("listEmailsBTN")
            or request.POST.get("updateItemBTN")
            or request.POST.get("deleteItemBTN")
        )
    ):
        originalSourceEmail = formDomain.cleaned_data.get("originalSourceEmail", "")
        originalDestinationEmail = formDomain.cleaned_data.get(
            "originalDestinationEmail", ""
        )
        sourceEmail = formDomain.cleaned_data.get("sourceEmail", "")
        destinationEmail = formDomain.cleaned_data.get("destinationEmail", "")
        domainName = formDomain.cleaned_data.get("domainSelect", "")
        # save operator in cookie session
        operator = formDomain.cleaned_data.get("operator")
        request.session["operator"] = operator
        # add email
        if (
            request.POST.get("updateItemBTN")
            and request.POST.get("originalSourceEmail") == " "
        ):
            result = add_alias_to_webhosting(
                sourceEmail,
                domainName,
                destinationEmail,
            )
            if not result:
                messages.add_message(request, messages.SUCCESS, "Completed")
            else:
                messages.add_message(request, messages.WARNING, result)
        # update email
        if (
            request.POST.get("updateItemBTN")
            and request.POST.get("originalSourceEmail") != " "
        ):
            result = update_alias_in_webhosting(
                originalSourceEmail,
                domainName,
                originalDestinationEmail,
                sourceEmail,
                destinationEmail,
            )
            if not result:
                messages.add_message(request, messages.SUCCESS, "Completed")
            else:
                messages.add_message(request, messages.WARNING, result)
        # delete email
        if request.POST.get("deleteItemBTN"):
            result = remove_alias_from_webhosting(
                originalSourceEmail,
                domainName,
                originalDestinationEmail,
            )
            if not result:
                messages.add_message(request, messages.SUCCESS, "Completed")
            else:
                messages.add_message(request, messages.WARNING, result)
    #
    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "isDisabled": "" if isUserExist else "disabled",
        "isUserExist": isUserExist,
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formSearchLogin": formSearchLogin,
        "formDomain": formDomain,
        "formEmailList": formEmailList,
    }
    return render(request, "webhosting/sample.html", context)
