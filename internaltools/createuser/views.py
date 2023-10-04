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
from canadapost import getIDsFromIndex, getIndexFromPostal, getAddressFromID


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
            if len(creditCardExpiry) > 0 and not isDateValid(creditCardExpiry):
                self.add_error("creditCardExpiry", "Date is invalid")
            if isDateValid(creditCardExpiry) and isDateExpired(creditCardExpiry):
                self.add_error("creditCardExpiry", "Credit card is expired")
            if isDateValid(creditCardExpiry):
                self.cleaned_data["creditCardExpiry"] = getLastDay(creditCardExpiry)
        return self.cleaned_data


def isDateValid(dateToCheck):
    try:
        formattedDate = datetime.strptime(dateToCheck, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def isDateExpired(dateToCheck):
    if isDateValid(dateToCheck):
        checkDate = datetime.strptime(dateToCheck, "%Y-%m-%d")
        todayDate = datetime.now()
        if todayDate > checkDate:
            return True
    return False


def getLastDay(dateToConvert):
    lastDay = dateToConvert
    if isDateValid(dateToConvert):
        formattedDate = datetime.strptime(dateToConvert, "%Y-%m-%d")
        nextMonth = formattedDate.replace(day=28) + timedelta(days=5)
        lastDay = nextMonth - timedelta(days=nextMonth.day)
    return lastDay.strftime("%Y-%m-%d")


def sanitizeLogin(loginName):
    loginSanitized = loginName if re.match(r"^[\w.-]{1,30}$", loginName) else ""
    return loginSanitized


def countConfirmedLoginName(loginToCheck):
    loginToCheckSanitized = sanitizeLogin(loginToCheck)
    loginFound = queryDBscalar(
        f"SELECT count(*) FROM UsersId where LoginName = lower('{loginToCheckSanitized}')"
    )
    return loginFound


def getUserInfo(loginName):
    usersDict = queryDBrow(
        """SELECT
          LoginName as 'loginName',
          FirstName as 'firstName',
          LastName as 'lastName',
          OrganizationName as 'organizationName',
          Address as 'address',
          City as 'city',
          State as 'state',
          PostalCode as 'postalCode',
          Country as 'country',
          HomePhone as 'homePhone',
          AccountNumber as 'accountNumber',
          isnull(Language, '') as 'language',
          isnull(PaymentMethod, '') as 'paymentMethod',
          CreditCardNumber as 'creditCardNumber',
          replace(convert(varchar,CreditCardExpiry,102),'.','-') as 'creditCardExpiry',
          BankName as 'bankName',
          CheckNumber as 'checkNumber',
          BankAccount as 'bankAccount',
          IdentificationCard as 'identificationCard',
          AuthorizationCode as 'authorizationCode',
          OperatingSystem as 'operatingSystem',
          Operator as 'operator',
          ReferredBy as 'referredBy',
          Notes as 'notes',
          replace(convert(varchar,DateJoined,102),'.','-') as "dateJoined"
      FROM
          UsersId
      WHERE
          LoginName = %s
      """,
        loginName,
    )
    strippedUsersDict = {
        key: value.strip() if isinstance(value, str) else value
        for key, value in usersDict.items()
    }
    return strippedUsersDict


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
        "loginName": "",
    }
    isUserExist = False
    formSearchLogin = FormSearchLogin(defaultData | request.GET.dict())
    formUserDetail = FormUserDetail(request.POST.dict())

    """ --- """
    """ GET request received """
    if formSearchLogin.is_valid():
        loginName = formSearchLogin.cleaned_data["loginName"]
        loginFound = countConfirmedLoginName(loginName)
        isUserExist = True if (str(loginFound) == "1") else False
        userDict = getUserInfo(loginName) if isUserExist else dict()
        formUserDetail = FormUserDetail(
            userDict | request.POST.dict() | {"loginName": loginName}
        )

    """ --- """
    """ Button Pressed LOOKUP postal code """
    if (
        request.method == "POST"
        and request.POST.get("postalCode")
        and request.POST.get("lookupAddress")
    ):
        indexID = getIndexFromPostal(request.POST.get("postalCode"))
        listOfAddresses = getIDsFromIndex(indexID)
        myChoices = [
            ("", "Refine address ..."),
        ]
        myChoices += [(k, v) for k, v in listOfAddresses.items()]
        formUserDetail.fields["addressSelect"].choices = myChoices
        formUserDetail.fields["postalCode"].initial = request.POST.get("postalCode")
    """ --- """
    """ Button Pressed APPLY postal code """
    if (
        request.method == "POST"
        and request.POST.get("addressSelect")
        and request.POST.get("applyAddress")
    ):
        postalAddress = getAddressFromID(request.POST.get("addressSelect"))
        if len(postalAddress) >= 5:
            newAddress = {
                "address": postalAddress["Line1"],
                "city": postalAddress["City"],
                "state": postalAddress["ProvinceCode"],
                "country": "Canada",
                "postalCode": postalAddress["PostalCode"],
            }
            formUserDetail = FormUserDetail(request.POST.dict() | newAddress)

    """ --- """
    """ Button Pressed UpdateUser """
    if request.method == "POST" and request.POST.get("updateUser"):
        initialUserDetail = FormUserDetail(request.POST.dict())
        if initialUserDetail.is_valid():
            submitToAladin(initialUserDetail.cleaned_data)
            messages.add_message(
                request, messages.SUCCESS, f"User info has been updated"
            )
            # freeze the form
            isUserExist = not isUserExist
        else:
            messages.add_message(request, messages.WARNING, f"Form is still INVALID")
        """
        # rebuilding form using POST + cleaned_data
        # .cleaned_data generated from is_valid call
        # .cleaned_data contains updated fields from validation such as ccexpiry
        # notice .cleaned_data does not contain fields wit errors, we need original POSTed data
        """
        formUserDetail = FormUserDetail(
            request.POST.dict() | initialUserDetail.cleaned_data
        )

    # example query using django models
    # add this: from .models import UsersId
    # myResult = UsersId.objects.using('db2')
    # myResultList = (myResult.values()[0]['LoginName'])

    loginName = request.GET.get("loginName")
    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "buttonStyle": "success" if isUserExist else "secondary",
        "isValid": "isValid" if isUserExist else "is-invalid",
        "isDisabled": "disabled" if isUserExist else "",
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formSearchLogin": formSearchLogin,
        "formUserDetail": formUserDetail,
    }
    return render(request, "createuser/sample.html", context)
