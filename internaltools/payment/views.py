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
import moneris


class FormPayment(forms.Form):
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
    invoiceNumber = forms.DecimalField(
        label="Invoice Number",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        max_digits=20,
        decimal_places=10,
    )
    refundPassword = forms.CharField(
        label="Refund Password",
        widget=forms.PasswordInput(
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
                regex="^ *moro *$",
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
    PAYMENT_CHOICE = [
        ("", "choose"),
        ("cheque--", "Cheque"),
        ("mo--", "Money Order"),
        ("interac--", "Interac"),
        ("bank--", "Bank"),
        ("cash--", "Cash"),
        ("cc--", "Credit Card"),
    ]
    paymentType = forms.ChoiceField(
        choices=PAYMENT_CHOICE,
        initial="",
        label="Payment Type",
        widget=forms.Select(
            attrs={
                "class": "form-control form-select",
            }
        ),
        required=False,
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
                # regex="^[\w. &'<>;+$()/=@,:*#\"\\[\]-]*$",
                regex="^[\w. +$()/=@,:*#-]*$",
                message="invalid characters",
            )
        ],
    )
    amount = forms.DecimalField(
        label="Amount $",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=True,
        max_digits=6,
        decimal_places=2,
    )
    creditCardNumber = forms.CharField(
        label="Credit Card Number",
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
                regex="^[0-9 ]{16,19}$",
                message="must be empty or a credit card number 4111111111111111",
            )
        ],
    )
    creditCardExpiry = forms.CharField(
        label="Credit Card Expiry",
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
                regex="^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
                message="YYYY-MM-DD ex:2030-11-30",
            )
        ],
    )
    chequeNumber = forms.CharField(
        label="Cheque Number",
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
                regex="^[\w. &'-]*[\w.]$",
                message="invalid characters",
            )
        ],
    )

    def clean(self):
        cleaned_data = super().clean()
        creditCardNumber = cleaned_data.get("creditCardNumber")
        creditCardExpiry = cleaned_data.get("creditCardExpiry")
        if (
            creditCardNumber is not None
            and creditCardExpiry is not None
            and len(creditCardNumber + creditCardExpiry) > 0
        ):
            if len(creditCardNumber) == 0 or len(creditCardExpiry) == 0:
                msg = "provide all credit card info or none"
                self.add_error("creditCardNumber", msg)
                self.add_error("creditCardExpiry", msg)
            if len(creditCardExpiry) > 0 and not commons.isDateValid(creditCardExpiry):
                self.add_error("creditCardExpiry", "Date is invalid")
            if commons.isDateValid(creditCardExpiry) and commons.isDateExpired(
                creditCardExpiry
            ):
                self.add_error("creditCardExpiry", "Credit card is expired")
            if commons.isDateValid(creditCardExpiry):
                self.cleaned_data["creditCardExpiry"] = commons.getLastDay(
                    creditCardExpiry
                )
        amount = cleaned_data.get("amount")
        refundPassword = cleaned_data.get("refundPassword")
        if (
            refundPassword is not None
            and amount is not None
            and float(amount) < 0
            and len(refundPassword) == 0
        ):
            msg = "refunds needs a password"
            self.add_error("refundPassword", msg)
            self.add_error("amount", msg)
        #
        return self.cleaned_data


def submit_payment(paymentDict):
    creditCardNumber = paymentDict.get("creditCardNumber")
    creditCardExpiry = paymentDict.get("creditCardExpiry")
    amount = paymentDict.get("amount")
    amount = commons.getNumberFormatted(amount)
    # make moneris payment
    if creditCardNumber and creditCardExpiry and amount:
        creditCard = {
            "Num": creditCardNumber,
            "ExpMonth": creditCardExpiry[5:7],
            "ExpYear": creditCardExpiry[2:4],
            "Amount": str(amount),
        }
        """
        # FAKE monerisResult
        monerisResult = {
            "result": "DECLINED",
            "orderid": "1697908680",
            "reference": "661338780012670080 M",
            "authorization": "000000  ",
            "response": "073",
            "message": "NO ROUTE           *                    =",
            "transactionTime": "13:18:00",
            "transactionDate": "2023-10-21",
            "transactionType": "Purchase",
            "amount": "$0.01",
        }
        """
        monerisResult = moneris.pay(creditCard)
        monerisApproved = monerisResult.get("result") == "APPROVED"
        monerisString = creditCardNumber + " " + creditCardExpiry + " "
        monerisString += "Ref: " + monerisResult.get("result", "")
        monerisString += "-" + monerisResult.get("orderid", "")
        monerisString += "-" + monerisResult.get("reference", "")
        monerisString += "-" + monerisResult.get("response", "")
        monerisString += " " + monerisResult.get("amount", "")
        monerisString += " Auth: " + monerisResult.get("authorization", "")
        monerisString += " " + monerisResult.get("message", "")
        paymentDict["specialNote"] = monerisString + paymentDict.get("specialNote", "")
        paymentDict["specialNote"] = paymentDict.get("specialNote", "")[0:200]
        if not monerisApproved:
            paymentDict["amount"] = 0
    result = record_payment_on_aladin(paymentDict)
    return result


def record_payment_on_aladin(paymentDict):
    invoiceNumber = paymentDict.get("invoiceNumber")
    if invoiceNumber:
        invoiceNumber = commons.get_invoicenumber_from_obfuscated_number(invoiceNumber)
    querySQL = """
    EXECUTE INV_MakePayment
        @LoginName = %(loginName)s
        ,@InvoiceNumber = %(invoiceNumber)d
        ,@PaidAmount = %(amount)d
        ,@ChkNum = %(chequeNumber)s
        ,@Operator = %(operator)s
        ,@DebugLevel = %(debugLevel)s
        ,@Comments = %(specialNote)s
    """
    paramSQL = {
        "loginName": str(paymentDict.get("loginName")),
        "invoiceNumber": invoiceNumber,
        "amount": paymentDict.get("amount"),
        "chequeNumber": str(paymentDict.get("chequeNumber", "")),
        "operator": str(paymentDict.get("operator", "")),
        "debugLevel": "1",
        "specialNote": paymentDict.get("paymentType", "")
        + paymentDict.get("specialNote", ""),
    }
    # print(f"DEBUG MESSAGE: {querySQL}")
    # print(f"DEBUG MESSAGE: {paramSQL}")
    result = queryDBall(querySQL, paramSQL)
    return result


def get_payment_logs():
    querySQL = """
    SET ROWCOUNT 30;
    SELECT TranDate
           ,TranID
           ,Desc1
           ,Desc2
           ,LoginName
           ,Operator
           ,PaidAmount
    FROM TransactionHistory
    WHERE TranID between 11200 and 11201
    ORDER BY TranNum DESC;
    SET ROWCOUNT 0;
            """
    paramSQL = {}
    # print(f"DEBUG MESSAGE: {querySQL}")
    # print(f"DEBUG MESSAGE: {paramSQL}")
    result = queryDBall(querySQL, paramSQL)
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
    formPayment = FormPayment(defaultData)
    #
    # pre assign parameters
    loginName = defaultData.get("loginName")
    # item button was submitted
    if request.method == "POST" and request.POST.get("updateItemBTN"):
        formPayment = FormPayment(request.POST.dict())
        if formPayment.is_valid():
            loginName = formPayment.cleaned_data.get("loginName")
            confirmedLoginName = commons.get_loginname_from_database(loginName)
            if confirmedLoginName:
                # save operator login in cookie session
                request.session["loginName"] = confirmedLoginName
                request.session["operator"] = formPayment.cleaned_data.get("operator")
                # result = [{"ValidPayment": None, "SpecialNote": "testing"}]
                result = submit_payment(formPayment.cleaned_data)
                validPayment = result[0].get("ValidPayment")
                specialNote = result[0].get("SpecialNote")
                if validPayment:
                    messages.add_message(
                        request, messages.SUCCESS, f"{specialNote or '-'}"
                    )
                    operator = formPayment.cleaned_data.get("operator")
                    formPayment = FormPayment()
                    formPayment.fields["operator"].initial = operator
                else:
                    messages.add_message(
                        request, messages.WARNING, f"{specialNote or '-'}"
                    )
    #
    paymentLogs = get_payment_logs()
    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formPayment": formPayment,
        "paymentLogs": paymentLogs,
    }
    return render(request, "payment/sample.html", context)
