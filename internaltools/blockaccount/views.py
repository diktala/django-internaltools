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


class FormBlockAccount(forms.Form):
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
    CHOICES = [
        ("", "Select type"),
        ("set", "Block access"),
        ("reset", "Unblock access"),
    ]
    actionType = forms.ChoiceField(
        label="Choose Action",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
        choices=CHOICES,
        required=True,
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
                # regex="""^[\w. &'<>+$()/=@,:*#"\[\]-]*$""",
                regex="^[\w. +$()/=@,:*#-]*$",
                message="invalid characters",
            )
        ],
    )
    CHOICES = [
        ("1", "Yes"),
        ("0", "No"),
    ]
    unblockPossible = forms.ChoiceField(
        label="Allow to Unblock?",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
        choices=CHOICES,
        required=True,
    )
    CHOICES = [
        ("", "Select from List"),
        (
            "<en>Please provide a valid credit card number &amp; expiry date.<fr>Veuillez fournir un numéro de carte de crédit ainsi que la date d'expiration.",
            "Credit-Card",
        ),
        (
            "<en>Your subscription has ended.  please indicate if you already sent your payment<fr>Votre abonnement est expiré. Veuillez indiquer la date de votre paiement",
            "Membership expired",
        ),
        (
            "<en>You have an outstanding balance. Please indicate the date of your last payment<fr>Vous avez un solde dû. A quelle date avez-vous envoyé votre paiement?",
            "outstanding balance",
        ),
        (
            "<en>spam messages are sent from your connection.  You may need to check your computer or router for possible virus.<fr>Nous recevons du spam de votre connexion, Ils se peut que votre ordinateur ou routeur soit infecté.",
            "Sending spam",
        ),
        (
            "<en>We must receive the payment before the end of the month in order to keep the account opened.<fr>Le paiement doit être recu avant la fin du mois afin de  garder le compte ouvert.",
            "Account will close",
        ),
    ]
    standardPrompt = forms.ChoiceField(
        label="Standard Prompt",
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
        choices=CHOICES,
        required=True,
    )
    englishPrompt = forms.CharField(
        label="Override English Prompt",
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
                regex="""^[\w. &'<>+;$()/=@,:*#"\[\]-]*$""",
                message="invalid characters",
            )
        ],
    )
    frenchPrompt = forms.CharField(
        label="Override French Prompt",
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
                regex="""^[\w. &'<>+;$()/=@,:*#"\[\]-]*$""",
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


def submit_to_aladin(loginName, blockUser):
    standardPrompt = blockUser.get("standardPrompt", "")
    englishPrompt = blockUser.get("englishPrompt", "")
    frenchPrompt = blockUser.get("frenchPrompt", "")
    if len(standardPrompt) > 0:
        englishPrompt = standardPrompt
        frenchPrompt = ""

    querySQL = """
        EXECUTE DelinquentUserSam
        @LoginName = %(loginName)s
        ,@Action = %(actionType)s
        ,@Operator = %(operator)s
        ,@Comments = %(specialNote)s
        ,@DebugLevel = %(debugLevel)d
        ,@QuestionToAskEn = %(englishPrompt)s
        ,@QuestionToAskFr = %(frenchPrompt)s
        ,@AllowedToUnblock = %(unblockPossible)s
    """
    paramSQL = {
        "loginName": loginName,
        "actionType": blockUser.get("actionType"),
        "operator": blockUser.get("operator"),
        "specialNote": blockUser.get("specialNote"),
        "debugLevel": 1,
        "englishPrompt": englishPrompt,
        "frenchPrompt": frenchPrompt,
        "unblockPossible": blockUser.get("unblockPossible"),
    }
    blockUserResult = queryDBall(querySQL, paramSQL)
    if (
        isinstance(blockUserResult, list)
        and len(blockUserResult) > 0
        and isinstance(blockUserResult[0], dict)
    ):
        result = blockUserResult[0].get("ResultInfo", "")
    else:
        result = ""
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
    formBlockAccount = FormBlockAccount(initial=defaultData)
    #
    # pre assign parameters
    loginName = defaultData.get("loginName")
    userInfo = list()
    freezeForm = False
    if request.method == "POST" and request.POST.get("updateItemBTN"):
        formBlockAccount = FormBlockAccount(request.POST.dict())
        if formBlockAccount.is_valid():
            operator = formBlockAccount.cleaned_data.get("operator")
            loginName = formBlockAccount.cleaned_data.get("loginName")
            loginName = commons.get_loginname_from_database(loginName)
            if loginName:
                request.session["loginName"] = loginName
                request.session["operator"] = operator
                blockUserResult = submit_to_aladin(
                    loginName, formBlockAccount.cleaned_data
                )
                messages.add_message(
                    request, messages.SUCCESS, f"Result: {blockUserResult}"
                )
                userInfo = get_user_info(loginName)
                freezeForm = True
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
        "formBlockAccount": formBlockAccount,
        "userInfo": userInfo[0] if len(userInfo) > 0 else None,
    }
    return render(request, "blockaccount/sample.html", context)
