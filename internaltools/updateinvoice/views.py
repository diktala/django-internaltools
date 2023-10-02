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


class FormInvoice(forms.Form):
    passe = forms.CharField(
        label="Password",
        widget=forms.TextInput(
            attrs={
                "placeholder": "password to unlock this form ...",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=1,
        max_length=20,
        validators=[
            RegexValidator(
                regex="^\w+$",
                message="invalid characters",
            )
        ],
    )
    invoiceNumber = forms.CharField(
        label="Invoice",
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
                regex="^[0-9.]+$",
                message="invalid characters",
            )
        ],
    )
    loginName = forms.CharField(
        label="Login Name",
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
                regex="^[a-z0-9][a-z0-9.-]*[a-z0-9]$",
                message="invalid characters",
            )
        ],
    )
    invoiceDate = forms.CharField(
        label="Invoice Date",
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
                regex="^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
                message="must be yyyy-mm-dd",
            )
        ],
    )
    dueDate = forms.CharField(
        label="Invoice Due Date",
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
        max_length=20,
        validators=[
            RegexValidator(
                regex="^[\w. &'<>;+$()/=@,:*#\"\\[\]-]*$",
                message="invalid characters",
            )
        ],
    )
    CHOICES = ["Printed","Reported","Paid","Canceled"]
    invoiceStatus = forms.ChoiceField(
        choices=[(op, op) for op in CHOICES],
        label="Invoice Status",
        widget=forms.Select(
            attrs={
                "class": "form-control form-select",
            }
        ),
        required=True,
        validators=[
            RegexValidator(
                regex="^(Printed)|(Reported)|(Paid)|(Canceled)$",
                message="must be one of (Printed)|(Reported)|(Paid)|(Canceled)",
            )
        ],
    )
    accountBalance = forms.DecimalField(
        label="Account Balance",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=True,
        max_digits=7,
        decimal_places=2,
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
    itemLine = forms.DecimalField(
        label="Item Line",
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
    itemCode = forms.ChoiceField(
        choices=[("-", "-")],
        initial="-",
        label="Item Code",
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
    quantity = forms.DecimalField(
        label="Quantity",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        max_digits=6,
        decimal_places=2,
    )
    lineNote = forms.CharField(
        label="Line Note",
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
                regex="^[\w. &'<>;+$()/=@,:*#\"\\[\]-]*$",
                message="invalid characters",
            )
        ],
    )
    def clean(self):
        cleaned_data = super().clean()
        itemLine = cleaned_data.get("itemLine")
        itemCode = cleaned_data.get("itemCode")
        quantity = cleaned_data.get("quantity")
        """
        """
        if (
            itemLine is not None
            and itemCode is not None
            and quantity is not None
        ):
            self.add_error("itemLine", 'some error for todo ....')
            self.cleaned_data["lineNote"] = " .......................... "
        return self.cleaned_data


def getInvoice(login_or_invoice = ''):
    querySQL = """EXECUTE wwwMaintenance.dbo.DisplayInvoice 2, @InvoiceNumberVar = %(InvoiceNumberVar)s"""
    paramSQL = { "InvoiceNumberVar": str(login_or_invoice) }
    invoiceDict = queryDBrow( querySQL, paramSQL )
    strippedInvoiceDict = {key: value.strip() if isinstance(value, str) else value for key, value in invoiceDict.items()}
    return strippedInvoiceDict


def getInvoiceDetail(login_or_invoice = ''):
    querySQL = """EXECUTE wwwMaintenance.dbo.DisplayInvoice 3, @InvoiceNumberVar = %(InvoiceNumberVar)s"""
    paramSQL = { "InvoiceNumberVar": str(login_or_invoice) }
    invoiceDict = queryDBall( querySQL, paramSQL )
    return invoiceDict


def submitToAladin(invoiceDict):
    updateAladinSQL1 = f"""
        EXECUTE UpdateInvoice
            @LoginName = %(loginName)s
            , @FirstName = %(firstName)s
            , @LastName = %(lastName)s
            , @OrganizationName = %(organizationName)s
            , @Address = %(address)s
            , @City = %(city)s
            , @State = %(state)s
            , @PostalCode = %(postalCode)s
            , @Country = %(country)s
            , @HomePhone = %(homePhone)s
            , @OperatingSystem = %(operatingSystem)s
            , @AccountNumber = %(accountNumber)s
            , @PaymentMethod = %(paymentMethod)s
            , @Membership = %(membership)s
            , @CreditCardExpiry = %(creditCardExpiry)s
            , @CreditCardNumber = %(creditCardNumber)s
            , @Notes = %(notes)s
            , @DateJoined = %(dateJoined)s
            , @NextBilling = %(nextBilling)s
            , @AccountSetupBy = %(accountSetupBy)s
            , @ReferredBy = %(referredBy)s
            , @GovID = %(govId)s
            , @GovConfirmation = %(govConfirmation)s
            , @GovAmount = %(govAmount)s
            , @OneTimeCharge = %(oneTimeCharge)s
            , @OneTimeQty = %(oneTimeQty)s
            , @Language = %(language)s
            , @DebugLevel = %(debugLevel)d
            , @Operator = %(operator)s
    """
    updateAladinParam1 = {
        "loginName": invoiceDict["loginName"],
        "firstName": invoiceDict["firstName"],
        "lastName": invoiceDict["lastName"],
        "organizationName": invoiceDict["organizationName"],
        "address": invoiceDict["address"],
        "city": invoiceDict["city"],
        "state": invoiceDict["state"],
        "postalCode": invoiceDict["postalCode"],
        "country": invoiceDict["country"],
        "homePhone": invoiceDict["homePhone"],
        "operatingSystem": invoiceDict["operatingSystem"],
        "accountNumber": invoiceDict["accountNumber"],
        "paymentMethod": invoiceDict["paymentMethod"],
        "membership": "",
        "creditCardExpiry": invoiceDict["creditCardExpiry"],
        "creditCardNumber": invoiceDict["creditCardNumber"],
        "notes": invoiceDict["notes"],
        "dateJoined": invoiceDict["dateJoined"],
        "nextBilling": "",
        "accountSetupBy": "",
        "referredBy": invoiceDict["referredBy"],
        "govId": "",
        "govConfirmation": "",
        "govAmount": "",
        "oneTimeCharge": "",
        "oneTimeQty": "",
        "language": invoiceDict["language"],
        "debugLevel": "1",
        "operator": invoiceDict["operator"],
    }
    print(f"DEBUG MESSAGE: {createAladinSQL1}")
    print(f"DEBUG MESSAGE: {createAladinParam1}")
    # queryDBall(updateAladinSQL1, updateAladinParam1)


def index(request):
    defaultData = {
        "loginName": request.GET.get("loginName") or "",
    }
    formSearchLogin = FormSearchLogin(defaultData)
    loginName = defaultData.get("loginName")
    debugMessage = f"login: {loginName}"
    isUserExist = False
    # formUserDetail.fields["postalCode"].initial = request.POST.get("postalCode")
    formInvoice = FormInvoice()
    invoiceDetailDict = dict()
    """ GET request received """
    if formSearchLogin.is_valid():
        loginName = formSearchLogin.cleaned_data["loginName"]
        # confirmedLoginName = commons.get_loginname_from_database(loginName)
        invoiceDict = getInvoice(loginName)
        if invoiceDict:
            isUserExist = True
            formInvoice.fields["loginName"].initial = invoiceDict.get("LoginName")
            formInvoice.fields["invoiceNumber"].initial = invoiceDict.get("InvoiceNumber")
            formInvoice.fields["invoiceDate"].initial = commons.getDateFormatted(invoiceDict.get("InvoiceDate"))
            formInvoice.fields["dueDate"].initial = commons.getDateFormatted(invoiceDict.get("DueDate"))
            formInvoice.fields["specialNote"].initial = invoiceDict.get("SpecialNote")
            formInvoice.fields["invoiceStatus"].initial = invoiceDict.get("InvoiceStatus")
            # TODO: make function for accountbalance
            formInvoice.fields["accountBalance"].initial = str(invoiceDict.get("AccountBalance"))[0:-2]
            invoiceDetailDict = getInvoiceDetail(loginName)
            debugMessage = f"confirmed entered:{loginName} {invoiceDict.get('LoginName')} "
    """ --- """
    if (
        request.method == "POST"
    ):
        formInvoice = FormInvoice( request.POST.dict() )
    #
    urlQuery = f"LoginName={loginName}"
    context = {
        "debugMessage": debugMessage,
        "loginName": loginName,
        "isDisabled": "" if isUserExist else "disabled",
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formSearchLogin": formSearchLogin,
        "formInvoice": formInvoice,
        "invoiceDetailDict": invoiceDetailDict,
    }
    return render(request, "updateinvoice/sample.html", context)
