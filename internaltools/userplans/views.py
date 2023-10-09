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


class FormPlans(forms.Form):
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
    lineID = forms.DecimalField(
        widget=forms.HiddenInput(
            attrs={
                "class": "form-control",
            }
        ),
        required=False,
        max_digits=8,
        decimal_places=0,
    )
    planName = forms.ChoiceField(
        choices=[("-", "-")],
        initial="-",
        label="Plan Name",
        widget=forms.Select(
            attrs={
                "class": "form-control form-select",
            }
        ),
        required=False,
        validators=[
            RegexValidator(
                regex="^[\w0-9. /-]+$",
                message="invalid characters",
            )
        ],
    )
    nextBilling = forms.CharField(
        label="Next Billing",
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
                message="must be yyyy-mm-dd",
            )
        ],
    )
    quantityOverride = forms.DecimalField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        max_digits=5,
        decimal_places=2,
    )
    maximumRepetition = forms.DecimalField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        max_digits=3,
        decimal_places=0,
    )
    planExpires = forms.CharField(
        label="Plan Expires",
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
                message="must be yyyy-mm-dd",
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
        max_length=200,
        validators=[
            RegexValidator(
                regex="^[\w. &'<>;+$()/=@,:*#\"\\[\]-]*$",
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


def get_user_plans(loginName=""):
    querySQL = (
        """EXECUTE UpdateUsersPlans @LoginName = %(loginName)s"""
    )
    paramSQL = {"loginName": str(loginName)}
    planDict = queryDBall(querySQL, paramSQL)
    return planDict


def get_all_plans():
    querySQL = """EXECUTE DisplayInvoice 7"""
    planDict = queryDBall(querySQL)
    return planDict


def submitToAladin(planDict):
    updateAladinSQL1 = f"""
        EXECUTE UpdateUsersPlans
            @LineID = %(lineID)s
            , @LoginName = %(loginName)s
            , @CurrentPlan = %(planName)s
            , @QuantityOverride = %(quantityOverride)s
            , @NextBilling = %(nextBilling)s
            , @PlanExpires = %(planExpires)s
            , @MaximumRepetition = %(maximumRepetition)s
            , @DomainName = %(specialNote)s
            , @Operator = %(operator)s
            , @DebugLevel = %(debugLevel)d
    """
    updateAladinParam1 = {
        "lineID": planDict["lineID"],
        "loginName": planDict["loginName"],
        "planName": planDict["planName"],
        "quantityOverride": planDict["quantityOverride"],
        "nextBilling": planDict["nextBilling"],
        "planExpires": planDict["planExpires"],
        "maximumRepetition": planDict["maximumRepetition"],
        "specialNote": planDict["specialNote"],
        "operator": planDict["operator"],
        "debugLevel": 1,
    }
    print(f"DEBUG MESSAGE: {updateAladinSQL1}")
    print(f"DEBUG MESSAGE: {updateAladinParam1}")
    # queryDBall(updateAladinSQL1, updateAladinParam1)


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
    #
    # pre assign parameters
    loginName = defaultData.get("loginName")
    isUserExist = False
    # dict_of_forms contains a form for each plan
    dict_of_forms = dict()
    # get list of all plans to populate drop down choices
    allPlansDict = get_all_plans()
    itemChoices = [
        (item.get("CurrentPlan"), item.get("CurrentPlan")) for item in allPlansDict
    ]
    itemChoices.insert(0, ("", "Select plan"))
    itemChoices.append(("RemovePlan", "Remove plan"))
    # Check if valid login request received
    if formSearchLogin.is_valid():
        loginName = formSearchLogin.cleaned_data.get("loginName")
        userPlans = get_user_plans(loginName)
        if userPlans:
            # found user plans for this user
            isUserExist = True
            # store in cookie session
            request.session['loginName'] = loginName
            emptyUserPlan = {
                "LoginName": loginName,
                "ShortNextBilling": "",
                "ShortPlanExpires": "",
                "LineID": "",
                "CurrentPlan": "",
                "QuantityOverride": "",
                "NextBilling": "",
                "PlanExpires": "",
                "MaximumRepetition": "",
                "DomainName": "",
                "RecordModified": "",
            }
            userPlans.append(emptyUserPlan)
            # each item in userPlans becomes its own html form
            for each_item in userPlans:
                form = FormPlans()
                form.fields["loginName"].initial = each_item.get("LoginName")
                form.fields["lineID"].initial = each_item.get("LineID")
                form.fields["planName"].choices = itemChoices
                form.fields["planName"].initial = each_item.get("CurrentPlan")
                form.fields["nextBilling"].initial = commons.getDateFormatted(
                    each_item.get("NextBilling")
                )
                form.fields["quantityOverride"].initial = each_item.get(
                    "QuantityOverride"
                )
                form.fields["maximumRepetition"].initial = each_item.get(
                    "MaximumRepetition"
                )
                form.fields["planExpires"].initial = commons.getDateFormatted(
                    each_item.get("PlanExpires")
                )
                form.fields["specialNote"].initial = each_item.get("DomainName")
                form.fields["operator"].initial = request.session.get("operator")
                dict_of_forms[str(each_item.get("LineID"))] = form
    """ --- """
    # update line item button was submitted
    if request.method == "POST" and request.POST.get("updateItemBTN"):
        # update the correct form from the list
        lineID = request.POST.get("lineID")
        dict_of_forms[lineID] = FormPlans(request.POST.dict())
        form_being_updated = dict_of_forms.get(lineID)
        form_being_updated.fields["planName"].choices = itemChoices
        if form_being_updated.is_valid():
            messages.add_message(request, messages.SUCCESS, f"Item is VALID")
            submit_invoice_to_aladin = form_being_updated.cleaned_data
            submitToAladin(submit_invoice_to_aladin)
            # store in cookie session
            request.session['operator'] = form_being_updated.cleaned_data.get("operator")
        else:
            messages.add_message(request, messages.WARNING, f"Item is still INVALID")
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
        "dict_of_forms": dict_of_forms,
    }
    return render(request, "userplans/sample.html", context)
