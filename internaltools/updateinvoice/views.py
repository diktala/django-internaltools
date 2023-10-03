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
        label="Invoice / Login",
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
        required=False,
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
                "class": "form-control-plaintext",
                "readonly": "readonly",
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
                "class": "form-control-plaintext",
                "readonly": "readonly",
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
    CHOICES = ["Printed", "Reported", "Paid", "Canceled"]
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
    originalItemLine = forms.DecimalField(
        label="Original Item Line",
        widget=forms.HiddenInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        max_digits=3,
        decimal_places=0,
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
        max_length=30,
        validators=[
            RegexValidator(
                regex="^[\w. &'<>;+$()/=@,:*#\"\\[\]-]*$",
                message="invalid characters",
            )
        ],
    )
    """
    def clean(self):
        cleaned_data = super().clean()
        itemLine = cleaned_data.get("itemLine")
        itemCode = cleaned_data.get("itemCode")
        quantity = cleaned_data.get("quantity")
        if (
            itemLine is not None
            and itemCode is not None
            and quantity is not None
        ):
            self.add_error("itemLine", 'some error for todo ....')
            self.cleaned_data["lineNote"] = " .......................... "
        return self.cleaned_data
    """


def getInvoice(login_or_invoice=""):
    querySQL = """EXECUTE wwwMaintenance.dbo.DisplayInvoice 2, @InvoiceNumberVar = %(InvoiceNumberVar)s"""
    paramSQL = {"InvoiceNumberVar": str(login_or_invoice)}
    invoiceDict = queryDBrow(querySQL, paramSQL)
    strippedInvoiceDict = {
        key: value.strip() if isinstance(value, str) else value
        for key, value in invoiceDict.items()
    }
    return strippedInvoiceDict


def getInvoiceDetail(login_or_invoice=""):
    querySQL = """EXECUTE wwwMaintenance.dbo.DisplayInvoice 3, @InvoiceNumberVar = %(InvoiceNumberVar)s"""
    paramSQL = {"InvoiceNumberVar": str(login_or_invoice)}
    invoiceDict = queryDBall(querySQL, paramSQL)
    return invoiceDict


def getItemCodes():
    querySQL = """EXECUTE wwwMaintenance.dbo.DisplayInvoice 5 """
    itemDict = queryDBall(querySQL)
    return itemDict


def getAllInvoices(login_or_invoice=""):
    querySQL = """EXECUTE wwwMaintenance.dbo.DisplayInvoice 6, @InvoiceNumberVar = %(InvoiceNumberVar)s"""
    paramSQL = {"InvoiceNumberVar": str(login_or_invoice)}
    list_of_invoices = queryDBall(querySQL, paramSQL)
    return list_of_invoices


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
    # debugMessage = f"login: {loginName}"
    isUserExist = False
    formInvoice = FormInvoice()
    invoiceDetailDict = dict()
    list_of_all_invoices = dict()
    list_of_items = []
    """ Check if valid login or invoicenumber request received """
    if formSearchLogin.is_valid():
        invoice_or_login = formSearchLogin.cleaned_data["loginName"]
        list_of_all_invoices = getAllInvoices(invoice_or_login)
        invoiceDict = getInvoice(invoice_or_login)
        if invoiceDict:
            isUserExist = True
            formInvoice.fields["loginName"].initial = invoiceDict.get("LoginName")
            formInvoice.fields["invoiceNumber"].initial = invoiceDict.get(
                "InvoiceNumber"
            )
            formInvoice.fields["invoiceDate"].initial = commons.getDateFormatted(
                invoiceDict.get("InvoiceDate")
            )
            formInvoice.fields["dueDate"].initial = commons.getDateFormatted(
                invoiceDict.get("DueDate")
            )
            formInvoice.fields["specialNote"].initial = invoiceDict.get("SpecialNote")
            formInvoice.fields["invoiceStatus"].initial = invoiceDict.get(
                "InvoiceStatus"
            )
            formInvoice.fields["accountBalance"].initial = commons.getNumberFormatted(
                invoiceDict.get("AccountBalance")
            )
            # debugMessage = f"confirmed entered:{invoice_or_login} {invoiceDict.get('LoginName')} "
            itemDict = getItemCodes()
            itemChoices = [
                (item.get("ItemCode"), item.get("ItemCode")) for item in itemDict
            ]
            itemChoices.insert(0, ("", ""))
            invoiceDetailDict = getInvoiceDetail(invoice_or_login)
            for each_item in invoiceDetailDict:
                form = FormInvoice()
                form.fields["loginName"].initial = invoiceDict.get("LoginName")
                form.fields["invoiceNumber"].initial = invoiceDict.get("InvoiceNumber")
                form.fields["invoiceDate"].initial = commons.getDateFormatted(
                    invoiceDict.get("InvoiceDate")
                )
                form.fields["dueDate"].initial = commons.getDateFormatted(
                    invoiceDict.get("DueDate")
                )
                form.fields["specialNote"].initial = invoiceDict.get("SpecialNote")
                form.fields["invoiceStatus"].initial = invoiceDict.get("InvoiceStatus")
                form.fields["accountBalance"].initial = commons.getNumberFormatted(
                    invoiceDict.get("AccountBalance")
                )
                form.fields["originalItemLine"].initial = each_item.get("ItemNumber")
                form.fields["itemLine"].initial = each_item.get("ItemNumber")
                form.fields["itemCode"].choices = itemChoices
                form.fields["itemCode"].initial = each_item.get("ItemCode")
                form.fields["quantity"].initial = each_item.get("QuantitySold")
                form.fields["lineNote"].initial = each_item.get("LineNote")
                list_of_items.append(form)
    """ --- """
    if request.method == "POST" and request.POST.get("updateInvoiceBTN"):
        formInvoice = FormInvoice(request.POST.dict())
        if formInvoice.is_valid():
            messages.add_message(request, messages.SUCCESS, f"Form is VALID")
        else:
            messages.add_message(request, messages.WARNING, f"Form is still INVALID")

    if request.method == "POST" and request.POST.get("updateItemBTN"):
        itemLine = request.POST.get("originalItemLine")
        itemIndex = int(itemLine) - 1
        list_of_items[itemIndex] = FormInvoice(request.POST.dict())
        list_of_items[itemIndex].fields["itemCode"].choices = itemChoices
        itemForm = list_of_items[itemIndex]
        # itemCodeValue = itemForm.fields["itemCode"].initial
        # messages.add_message(request, messages.INFO, f"Item is {itemLine} - {itemCodeValue}")
        if itemForm.is_valid():
            messages.add_message(request, messages.SUCCESS, f"Item is VALID")
        else:
            messages.add_message(request, messages.WARNING, f"Item is still INVALID")
    #
    urlQuery = f"LoginName={loginName}"
    context = {
        # "debugMessage": debugMessage,
        "loginName": loginName,
        "isDisabled": "" if isUserExist else "disabled",
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formSearchLogin": formSearchLogin,
        "formInvoice": formInvoice,
        "list_of_items": list_of_items,
        "invoiceDetailDict": invoiceDetailDict,
        "list_of_all_invoices": list_of_all_invoices,
    }
    return render(request, "updateinvoice/sample.html", context)
