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
    passe = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            # retain the value after POST
            render_value=True,
            attrs={
                "placeholder": "password to enable update functions ...",
                "class": "form-control",
            },
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


class FormInvoice(forms.Form):
    passe = forms.CharField(
        widget=forms.HiddenInput(
            attrs={
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
        max_length=250,
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
            @Passe = %(passe)s
            , @InvoiceNumber = %(invoiceNumber)s
            , @LoginName = %(loginName)s
            , @InvoiceDate = %(invoiceDate)s
            , @EndPeriodDate = %(dueDate)s
            , @SpecialNote = %(specialNote)s
            , @InvoiceStatus = %(invoiceStatus)s
            , @UpdateItemNumber = %(originalItemLine)s
            , @ItemNumber = %(itemLine)s
            , @ItemCode = %(itemCode)s
            , @QuantitySold = %(quantity)s
            , @LineNote = %(lineNote)s
            , @Operator = %(operator)s
            , @AccountBalance = %(accountBalance)s
            , @NextBilling = %(nextBilling)s
            , @DebugLevel = %(debugLevel)d
    """
    updateAladinParam1 = {
        "passe": invoiceDict["passe"],
        "invoiceNumber": invoiceDict["invoiceNumber"],
        "loginName": invoiceDict["loginName"],
        "invoiceDate": invoiceDict["invoiceDate"],
        "dueDate": invoiceDict["dueDate"],
        "specialNote": invoiceDict["specialNote"],
        "invoiceStatus": invoiceDict["invoiceStatus"],
        "originalItemLine": invoiceDict["originalItemLine"],
        "itemLine": invoiceDict["itemLine"],
        "itemCode": invoiceDict["itemCode"],
        "quantity": invoiceDict["quantity"],
        "lineNote": invoiceDict["lineNote"],
        "operator": invoiceDict["operator"],
        "accountBalance": invoiceDict["accountBalance"],
        "nextBilling": "",
        "debugLevel": 1,
    }
    print(f"DEBUG MESSAGE: {updateAladinSQL1}")
    print(f"DEBUG MESSAGE: {updateAladinParam1}")
    # queryDBall(updateAladinSQL1, updateAladinParam1)


def index(request):
    # get invoice or loginname from POST or from URL
    defaultData = {
        "loginName": request.POST.get("loginName")
        or request.GET.get("loginName")
        or request.GET.get("LoginName")
        or "",
        "passe": request.POST.get("passe") or "",
    }
    formSearchLogin = FormSearchLogin(defaultData)
    #
    # pre assign parameters
    loginName = defaultData.get("loginName")
    isUserExist = False
    formInvoice = FormInvoice()
    invoiceDetailList = list([])
    list_of_all_invoices = dict()
    # list_of_items contains a form for each itemLine
    list_of_items = dict()
    # Check if valid login or invoicenumber request received
    if formSearchLogin.is_valid():
        invoice_or_login = formSearchLogin.cleaned_data.get("loginName")
        password_of_form = formSearchLogin.cleaned_data.get("passe")
        list_of_all_invoices = getAllInvoices(invoice_or_login)
        invoiceDict = getInvoice(invoice_or_login)
        if invoiceDict:
            # found invoice for this user
            isUserExist = True
            formInvoice.fields["passe"].initial = password_of_form
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
            # populate list of itemCodes as drop down choices
            itemDict = getItemCodes()
            itemChoices = [
                (item.get("ItemCode"), item.get("ItemCode")) for item in itemDict
            ]
            itemChoices.insert(0, ("", ""))
            # get detail of this invoice store it in a list of forms
            invoiceDetailList = getInvoiceDetail(invoice_or_login)
            emptyItemDict = {
                "ItemNumber": "",
                "ItemCode": "",
                "QuantitySold": "",
                "LineNote": "",
            }
            invoiceDetailList.append(emptyItemDict)
            # each item in invoicedetail gets its own html form
            for each_item in invoiceDetailList:
                form = FormInvoice()
                form.fields["passe"].initial = password_of_form
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
                list_of_items[str(each_item.get("ItemNumber"))] = form
    """ --- """
    # update invoice button was submitted
    if request.method == "POST" and request.POST.get("updateInvoiceBTN"):
        formInvoice = FormInvoice(request.POST.dict())
        if formInvoice.is_valid():
            messages.add_message(request, messages.SUCCESS, f"Form is VALID")
            submit_invoice_to_aladin = formInvoice.cleaned_data
            submitToAladin(submit_invoice_to_aladin)
        else:
            messages.add_message(request, messages.WARNING, f"Form is still INVALID")

    """ --- """
    # update line item button was submitted
    if request.method == "POST" and request.POST.get("updateItemBTN"):
        # update the correct form from the list
        itemLine = request.POST.get("originalItemLine")
        list_of_items[itemLine] = FormInvoice(request.POST.dict())
        list_of_items.get(itemLine).fields["itemCode"].choices = itemChoices
        itemForm = list_of_items.get(itemLine)
        if itemForm.is_valid():
            messages.add_message(request, messages.SUCCESS, f"Item is VALID")
            submit_invoice_to_aladin = itemForm.cleaned_data
            submitToAladin(submit_invoice_to_aladin)
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
        "invoiceDetailList": invoiceDetailList,
        "list_of_all_invoices": list_of_all_invoices,
    }
    return render(request, "updateinvoice/sample.html", context)
