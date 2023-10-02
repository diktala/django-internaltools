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
        required=True,
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


class FormUserDetail(forms.Form):
    loginName = forms.CharField(
        widget=forms.HiddenInput(),
        required=True,
        min_length=1,
        max_length=20,
        validators=[
            RegexValidator(
                regex="^[a-z0-9][a-z0-9.-]*[a-z0-9]$",
            )
        ],
    )
    userPassword = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=1,
        max_length=12,
        validators=[
            RegexValidator(
                regex="^[a-z0-9._-]+$",
            )
        ],
    )
    firstName = forms.CharField(
        label="First Name",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=1,
        max_length=20,
        validators=[
            RegexValidator(
                regex="^[\w. &'-]*[\w]$",
                message="invalid characters",
            )
        ],
    )
    lastName = forms.CharField(
        label="Last Name",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=1,
        max_length=20,
        validators=[
            RegexValidator(
                regex="^[\w. &'-]*[\w]$",
                message="invalid characters",
            )
        ],
    )
    organizationName = forms.CharField(
        label="Organization Name",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=1,
        max_length=25,
        validators=[
            RegexValidator(
                regex="^[\w. &'-]*[\w.]$",
                message="invalid characters",
            )
        ],
    )
    address = forms.CharField(
        label="Address",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=1,
        max_length=30,
        validators=[
            RegexValidator(
                regex="^[\w. &',-]*[\w.]$",
                message="invalid characters",
            )
        ],
    )
    city = forms.CharField(
        label="City",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=1,
        max_length=20,
        validators=[
            RegexValidator(
                regex="^[\w. &'-]*[\w.]$",
                message="invalid characters",
            )
        ],
    )
    state = forms.CharField(
        label="State",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=1,
        max_length=20,
        validators=[
            RegexValidator(
                regex="^[\w. &'-]*[\w.]$",
                message="invalid characters",
            )
        ],
    )
    country = forms.CharField(
        label="Country",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=1,
        max_length=12,
        validators=[
            RegexValidator(
                regex="^[\w. &'-]*[\w.]$",
                message="invalid characters",
            )
        ],
    )
    postalCode = forms.CharField(
        label="Postal Code",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=1,
        max_length=20,
        validators=[
            RegexValidator(
                regex="^[A-Z][0-9][A-Z] [0-9][A-Z][0-9]$",
                message="must use a canadian postal code H1H 1H1",
            )
        ],
    )
    addressSelect = forms.ChoiceField(
        label="Select Address",
        choices=[
            ("", "<<< press Lookup"),
        ],
        initial="",
        widget=forms.Select(
            attrs={
                "class": "form-control form-select",
            }
        ),
        required=False,
    )
    homePhone = forms.CharField(
        label="Home Phone",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=1,
        max_length=12,
        validators=[
            RegexValidator(
                regex="^[0-9]{3} [0-9]{3} [0-9]{4}$",
                message="must use format 514 555 1212",
            )
        ],
    )
    accountNumber = forms.CharField(
        label="Account Number",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=1,
        max_length=20,
        validators=[
            RegexValidator(
                regex="^[0-9]{1,9}$",
                message="must be 9-digit ex. 800-555-1234 becomes 855512341",
            )
        ],
    )
    language = forms.ChoiceField(
        label="Language",
        choices=[
            ("", "FR"),
            ("EN", "EN"),
        ],
        initial="",
        widget=forms.Select(
            attrs={
                "class": "form-control form-select",
            }
        ),
        required=False,
        validators=[
            RegexValidator(
                regex="^EN$",
                message="Choose EN or empty",
            )
        ],
    )
    paymentMethod = forms.ChoiceField(
        label="Payment Method",
        choices=[
            ("VISA", "VISA"),
            ("MC", "MC"),
            ("", "Cheque"),
        ],
        initial="",
        widget=forms.Select(
            attrs={
                "class": "form-control form-select",
            }
        ),
        required=False,
        validators=[
            RegexValidator(
                regex="^VISA|MC$",
                message="Choose VISA or MC or empty",
            )
        ],
    )
    creditCardNumber = forms.CharField(
        label="Credit Card Number",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
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
                "placeholder": " ...",
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
    bankName = forms.CharField(
        label="Bank Name",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
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
    checkNumber = forms.CharField(
        label="Check Number",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
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
    bankAccount = forms.CharField(
        label="Bank Account",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
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
    identificationCard = forms.CharField(
        label="identificationCard",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
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
    authorizationCode = forms.CharField(
        label="Authorization Code",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
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
    operatingSystem = forms.CharField(
        label="Operating System",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=1,
        max_length=10,
        validators=[
            RegexValidator(
                regex="^[\w. &'-]*[\w.]$",
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
    referredBy = forms.CharField(
        label="Referred By",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
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
    notes = forms.CharField(
        label="Notes",
        widget=forms.TextInput(
            attrs={
                "placeholder": " ...",
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
    dateJoined = forms.CharField(
        label="Date Joined",
        widget=forms.HiddenInput(),
        required=False,
        min_length=1,
        max_length=10,
        validators=[
            RegexValidator(
                regex="^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
            )
        ],
    )

    def clean(self):
        cleaned_data = super().clean()
        paymentMethod = cleaned_data.get("paymentMethod")
        creditCardNumber = cleaned_data.get("creditCardNumber")
        creditCardExpiry = cleaned_data.get("creditCardExpiry")
        """ check credit card info """
        """
        """
        if (
            paymentMethod is not None
            and creditCardNumber is not None
            and creditCardExpiry is not None
        ):
            if len(creditCardNumber) == 0 and len(creditCardExpiry) > 0:
                msg = (
                    "provide a credit card number or remove the credit card expiry date"
                )
                self.add_error("creditCardNumber", msg)
                self.add_error("creditCardExpiry", msg)
            if len(creditCardNumber) > 0 and len(creditCardExpiry) == 0:
                msg = "provide a credit card expiry or remove the credit card number"
                self.add_error("creditCardNumber", msg)
                self.add_error("creditCardExpiry", msg)
            if len(creditCardExpiry) > 0 and not commons.isDateValid(creditCardExpiry):
                self.add_error("creditCardExpiry", "Date is invalid")
            if commons.isDateValid(creditCardExpiry) and commons.isDateExpired(creditCardExpiry):
                self.add_error("creditCardExpiry", "Credit card is expired")
            if commons.isDateValid(creditCardExpiry):
                self.cleaned_data["creditCardExpiry"] = commons.getLastDay(creditCardExpiry)
        return self.cleaned_data


def getInvoice(login_or_invoice = ''):
    querySQL = """EXECUTE wwwMaintenance.dbo.DisplayInvoice 2, @InvoiceNumberVar = %(InvoiceNumberVar)s"""
    paramSQL = { "InvoiceNumberVar": str(login_or_invoice) }
    invoiceDict = queryDBrow( querySQL, paramSQL )
    strippedInvoiceDict = {key: value.strip() if isinstance(value, str) else value for key, value in invoiceDict.items()}
    return strippedInvoiceDict


def submitToAladin(userInfoDict):
    updateAladinSQL1 = f"""
        EXECUTE UpdateUserFile
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
        "loginName": userInfoDict["loginName"],
        "firstName": userInfoDict["firstName"],
        "lastName": userInfoDict["lastName"],
        "organizationName": userInfoDict["organizationName"],
        "address": userInfoDict["address"],
        "city": userInfoDict["city"],
        "state": userInfoDict["state"],
        "postalCode": userInfoDict["postalCode"],
        "country": userInfoDict["country"],
        "homePhone": userInfoDict["homePhone"],
        "operatingSystem": userInfoDict["operatingSystem"],
        "accountNumber": userInfoDict["accountNumber"],
        "paymentMethod": userInfoDict["paymentMethod"],
        "membership": "",
        "creditCardExpiry": userInfoDict["creditCardExpiry"],
        "creditCardNumber": userInfoDict["creditCardNumber"],
        "notes": userInfoDict["notes"],
        "dateJoined": userInfoDict["dateJoined"],
        "nextBilling": "",
        "accountSetupBy": "",
        "referredBy": userInfoDict["referredBy"],
        "govId": "",
        "govConfirmation": "",
        "govAmount": "",
        "oneTimeCharge": "",
        "oneTimeQty": "",
        "language": userInfoDict["language"],
        "debugLevel": "1",
        "operator": userInfoDict["operator"],
    }
    updateAladinSQL2 = f"""
        UPDATE UsersId SET
        BankName = %(bankName)s
        , CheckNumber = %(checkNumber)s
        , BankAccount = %(bankAccount)s
        , IdentificationCard = %(identificationCard)s
        , AuthorizationCode = %(authorizationCode)s
        WHERE LoginName = %(loginName)s
    """
    updateAladinParam2 = {
        "bankName": userInfoDict["bankName"],
        "checkNumber": userInfoDict["checkNumber"],
        "bankAccount": userInfoDict["bankAccount"],
        "identificationCard": userInfoDict["identificationCard"],
        "authorizationCode": userInfoDict["authorizationCode"],
        "loginName": userInfoDict["loginName"],
    }
    createAladinSQL1 = f"""
        EXECUTE CreateUser
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
            , @Membership = %(membership)s
            , @Notes = %(notes)s
            , @UserPassword = %(userPassword)s
            , @OperatingSystem = %(operatingSystem)s
            , @AccountNumberChr = %(accountNumber)s
            , @PaymentMethod = %(paymentMethod)s
            , @CreditCardExpiry = %(creditCardExpiry)s
            , @CreditCardNumber = %(creditCardNumber)s
            , @CurrentPlan = %(currentPlan)s
            , @BankName = %(bankName)s
            , @CheckNumber = '%(CheckNumber)s'
            , @BankAccount = '%(BankAccount)s'
            , @IdentificationCard = '%(IdentificationCard)s'
            , @AuthorizationCode = '%(AuthorizationCode)s'
            , @Operator = %(operator)s
            , @ReferredBy = %(referredBy)s
            , @GovID = %(govId)s
            , @GovConfirmation = %(govConfirmation)s
            , @GovAmount = %(govAmount)s
    """
    createAladinParam1 = {
        "loginName": userInfoDict["loginName"],
        "firstName": userInfoDict["firstName"],
        "lastName": userInfoDict["lastName"],
        "organizationName": userInfoDict["organizationName"],
        "address": userInfoDict["address"],
        "city": userInfoDict["city"],
        "state": userInfoDict["state"],
        "postalCode": userInfoDict["postalCode"],
        "country": userInfoDict["country"],
        "homePhone": userInfoDict["homePhone"],
        "membership": "",
        "notes": userInfoDict["notes"],
        "userPassword": userInfoDict["userPassword"] or "some-long.1",
        "operatingSystem": userInfoDict["operatingSystem"],
        "accountNumber": f"{userInfoDict['homePhone'][0:1]}{userInfoDict['homePhone'][4:7]}{userInfoDict['homePhone'][8:12]}1",
        "paymentMethod": userInfoDict["paymentMethod"],
        "creditCardExpiry": userInfoDict["creditCardExpiry"],
        "creditCardNumber": userInfoDict["creditCardNumber"],
        "currentPlan": "Shipping",
        "bankName": userInfoDict["bankName"],
        "checkNumber": userInfoDict["checkNumber"],
        "bankAccount": userInfoDict["bankAccount"],
        "identificationCard": userInfoDict["identificationCard"],
        "authorizationCode": userInfoDict["authorizationCode"],
        "operator": userInfoDict["operator"],
        "referredBy": userInfoDict["referredBy"],
        "govId": "",
        "govConfirmation": "",
        "govAmount": "",
    }
    print(f"DEBUG MESSAGE: {createAladinSQL1}")
    print(f"DEBUG MESSAGE: {createAladinParam1}")
    # queryDBall(updateAladinSQL1, updateAladinParam1)
    # queryDBall(updateAladinSQL2, updateAladinParam2)


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
    """ GET request received """
    if formSearchLogin.is_valid():
        loginName = formSearchLogin.cleaned_data["loginName"]
        confirmedLoginName = commons.get_loginname_from_database(loginName)
        if confirmedLoginName:
            isUserExist = True
            loginName = confirmedLoginName
            invoiceDict = getInvoice(loginName)
            formInvoice.fields["loginName"].initial = invoiceDict.get("LoginName")
            formInvoice.fields["invoiceNumber"].initial = invoiceDict.get("InvoiceNumber")
            formInvoice.fields["invoiceDate"].initial = commons.getDateFormatted(invoiceDict.get("InvoiceDate"))
            # formInvoice.fields["invoiceDate"].initial = invoiceDict.get("InvoiceDate")
            formInvoice.fields["dueDate"].initial = commons.getDateFormatted(invoiceDict.get("DueDate"))
            formInvoice.fields["specialNote"].initial = invoiceDict.get("SpecialNote")
            formInvoice.fields["invoiceStatus"].initial = invoiceDict.get("InvoiceStatus")
            formInvoice.fields["accountBalance"].initial = invoiceDict.get("AccountBalance")
            debugMessage = f"confirmed login: {loginName}"
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
    }
    return render(request, "updateinvoice/sample.html", context)
