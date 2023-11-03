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
import commons
import secrets


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
                message="invalid characters",
            )
        ],
    )
    userPassword = forms.CharField(
        label="Assign Password",
        widget=forms.TextInput(
            attrs={
                "placeholder": "... auto generated ...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=5,
        max_length=12,
        validators=[
            RegexValidator(
                regex="^[a-z0-9._-]+$",
                message="invalid characters",
            )
        ],
    )
    firstName = forms.CharField(
        label="First Name",
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
                regex="^[A-Z0-9][\w. &'-]*[\w]$",
                message="invalid characters",
            )
        ],
    )
    lastName = forms.CharField(
        label="Last Name",
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
                regex="^[A-Z0-9][\w. &'-]*[\w]$",
                message="invalid characters",
            )
        ],
    )
    organizationName = forms.CharField(
        label="Organization Name",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=1,
        max_length=25,
        validators=[
            RegexValidator(
                regex="^[A-Z0-9][\w. &'-]*[\w.]$",
                message="invalid characters",
            )
        ],
    )
    address = forms.CharField(
        label="Address",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
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
                "placeholder": "...",
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
                "placeholder": "...",
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
                "placeholder": "...",
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
                "placeholder": "...",
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
                "placeholder": "...",
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
                "placeholder": "... auto generated ...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=1,
        max_length=20,
        validators=[
            RegexValidator(
                regex="^[0-9]{1,9}$",
                message="must be 9-digits ex. 800-555-1234 becomes 855512341",
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
    )
    paymentMethod = forms.ChoiceField(
        label="Payment Method",
        choices=[
            ("VISA", "VISA"),
            ("MC", "MC"),
            ("", "Other"),
        ],
        initial="",
        widget=forms.Select(
            attrs={
                "class": "form-control form-select",
            }
        ),
        required=False,
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
    bankName = forms.CharField(
        label="Bank Name",
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
    checkNumber = forms.CharField(
        label="Check Number",
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
                regex="^[0-9 ]+$",
                message="invalid characters",
            )
        ],
    )
    bankInstitution = forms.CharField(
        label="Bank Institution",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=1,
        max_length=3,
        validators=[
            RegexValidator(
                regex="^[\d]*$",
                message="only numbers allowed",
            )
        ],
    )
    bankTransit = forms.CharField(
        label="Bank Transit",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=1,
        max_length=6,
        validators=[
            RegexValidator(
                regex="^[\d]*$",
                message="only numbers allowed",
            )
        ],
    )
    bankAccount = forms.CharField(
        label="Bank Account",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=1,
        max_length=12,
        validators=[
            RegexValidator(
                regex="^[\d]*$",
                message="only numbers allowed",
            )
        ],
    )
    identificationCard = forms.CharField(
        label="identificationCard",
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
                regex="^[\w. :-]*[\w.]$",
                message="invalid characters",
            )
        ],
    )
    authorizationCode = forms.CharField(
        label="Authorization Code",
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
                regex="^[\w. -]*[\w.]$",
                message="invalid characters",
            )
        ],
    )
    operatingSystem = forms.CharField(
        label="Operating System",
        widget=forms.TextInput(
            attrs={
                "placeholder": "...",
                "class": "form-control",
            }
        ),
        required=False,
        min_length=1,
        max_length=10,
        validators=[
            RegexValidator(
                regex="^[\w. -]*$",
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
                regex="^[\w.-]*[\w.]$",
                message="invalid characters",
            )
        ],
    )
    referredBy = forms.CharField(
        label="Referred By",
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
                regex="^[\w. -]*[\w.]$",
                message="invalid characters",
            )
        ],
    )
    notes = forms.CharField(
        label="Notes",
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
                regex="""^[\w. &'<>+$()/=@,:*#"\[\]-]*$""",
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
            if commons.isDateValid(creditCardExpiry) and commons.isDateExpired(
                creditCardExpiry
            ):
                self.add_error("creditCardExpiry", "Credit card is expired")
            if commons.isDateValid(creditCardExpiry):
                self.cleaned_data["creditCardExpiry"] = commons.getLastDay(
                    creditCardExpiry
                )
        #
        bankInstitution = cleaned_data.get("bankInstitution")
        bankTransit = cleaned_data.get("bankTransit")
        bankAccount = cleaned_data.get("bankAccount")
        if (
            bankInstitution is not None
            and bankTransit is not None
            and bankAccount is not None
            and len(bankInstitution + bankTransit + bankAccount) > 0
        ):
            if (
                len(bankInstitution) == 0
                or len(bankTransit) == 0
                or len(bankAccount) == 0
            ):
                msg = "must provide full bank information or remove the info"
                self.add_error("bankInstitution", msg)
                self.add_error("bankTransit", msg)
                self.add_error("bankAccount", msg)
        #
        return self.cleaned_data


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
          BkAccount as 'bankAccount',
          BkBranchTransit as 'bankTransit',
          BkInstitutionId as 'bankInstitution',
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
        "loginName": userInfoDict.get("loginName"),
        "firstName": userInfoDict.get("firstName"),
        "lastName": userInfoDict.get("lastName"),
        "organizationName": userInfoDict.get("organizationName"),
        "address": userInfoDict.get("address"),
        "city": userInfoDict.get("city"),
        "state": userInfoDict.get("state"),
        "postalCode": userInfoDict.get("postalCode"),
        "country": userInfoDict.get("country"),
        "homePhone": userInfoDict.get("homePhone"),
        "operatingSystem": userInfoDict.get("operatingSystem"),
        "accountNumber": userInfoDict.get("accountNumber")
        or f"{userInfoDict.get('homePhone')[0:1]}{userInfoDict.get('homePhone')[4:7]}{userInfoDict.get('homePhone')[8:12]}1",
        "paymentMethod": userInfoDict.get("paymentMethod"),
        "membership": "",
        "creditCardExpiry": userInfoDict.get("creditCardExpiry"),
        "creditCardNumber": userInfoDict.get("creditCardNumber"),
        "notes": userInfoDict.get("notes"),
        "dateJoined": userInfoDict.get("dateJoined"),
        "nextBilling": "",
        "accountSetupBy": "",
        "referredBy": userInfoDict.get("referredBy"),
        "govId": "",
        "govConfirmation": "",
        "govAmount": "",
        "oneTimeCharge": "",
        "oneTimeQty": "",
        "language": userInfoDict.get("language"),
        "debugLevel": 1,
        "operator": userInfoDict.get("operator"),
    }
    updateAladinSQL2 = f"""
        UPDATE UsersId SET
        BankName = %(bankName)s
        , CheckNumber = %(checkNumber)s
        , BkAccount = %(bankAccount)s
        , BkInstitutionId = %(bankInstitution)s
        , BkBranchTransit = %(bankTransit)s
        , IdentificationCard = %(identificationCard)s
        , AuthorizationCode = %(authorizationCode)s
        WHERE LoginName = %(loginName)s
    """
    updateAladinParam2 = {
        "bankName": userInfoDict.get("bankName"),
        "checkNumber": userInfoDict.get("checkNumber"),
        "bankAccount": userInfoDict.get("bankAccount"),
        "bankInstitution": userInfoDict.get("bankInstitution"),
        "bankTransit": userInfoDict.get("bankTransit"),
        "identificationCard": userInfoDict.get("identificationCard"),
        "authorizationCode": userInfoDict.get("authorizationCode"),
        "loginName": userInfoDict.get("loginName"),
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
            , @CheckNumber = %(checkNumber)s
            , @BankAccount = %(bankAccount)s
            , @IdentificationCard = %(identificationCard)s
            , @AuthorizationCode = %(authorizationCode)s
            , @Operator = %(operator)s
            , @ReferredBy = %(referredBy)s
            , @GovID = %(govId)s
            , @GovConfirmation = %(govConfirmation)s
            , @GovAmount = %(govAmount)s
    """
    randomPassword = secrets.token_urlsafe(8).lower()
    createAladinParam1 = {
        "loginName": userInfoDict.get("loginName"),
        "firstName": userInfoDict.get("firstName"),
        "lastName": userInfoDict.get("lastName"),
        "organizationName": userInfoDict.get("organizationName"),
        "address": userInfoDict.get("address"),
        "city": userInfoDict.get("city"),
        "state": userInfoDict.get("state"),
        "postalCode": userInfoDict.get("postalCode"),
        "country": userInfoDict.get("country"),
        "homePhone": userInfoDict.get("homePhone"),
        "membership": "",
        "notes": userInfoDict.get("notes"),
        "userPassword": userInfoDict.get("userPassword") or randomPassword,
        "operatingSystem": userInfoDict.get("operatingSystem"),
        "accountNumber": f"{userInfoDict.get('homePhone')[0:1]}{userInfoDict.get('homePhone')[4:7]}{userInfoDict.get('homePhone')[8:12]}1",
        "paymentMethod": userInfoDict.get("paymentMethod"),
        "creditCardExpiry": userInfoDict.get("creditCardExpiry"),
        "creditCardNumber": userInfoDict.get("creditCardNumber"),
        "currentPlan": "",
        "bankName": userInfoDict.get("bankName"),
        "checkNumber": userInfoDict.get("checkNumber"),
        "bankAccount": "",
        "checkNumber": userInfoDict.get("checkNumber"),
        "identificationCard": userInfoDict.get("identificationCard"),
        "authorizationCode": userInfoDict.get("authorizationCode"),
        "operator": userInfoDict.get("operator"),
        "referredBy": userInfoDict.get("referredBy"),
        "govId": "",
        "govConfirmation": "",
        "govAmount": "",
    }
    loginName = userInfoDict.get("loginName")
    confirmedLoginName = commons.get_loginname_from_database(loginName)
    if confirmedLoginName:
        # user update
        queryDBall(updateAladinSQL1, updateAladinParam1)
        queryDBall(updateAladinSQL2, updateAladinParam2)
    else:
        # user create
        queryDBall(createAladinSQL1, createAladinParam1)
        queryDBall(updateAladinSQL2, updateAladinParam2)


def index(request):
    loginName = request.GET.get("loginName")
    defaultData = {
        "loginName": loginName or request.session.get("loginName") or "",
    }
    formSearchLogin = FormSearchLogin(defaultData)
    formUserDetail = FormUserDetail()
    isUserExist = False
    freezeForm = False

    """ --- """
    """ GET request received """
    if formSearchLogin.is_valid():
        loginName = formSearchLogin.cleaned_data.get("loginName")
        confirmedLoginName = commons.get_loginname_from_database(loginName)
        userDict = dict()
        if confirmedLoginName:
            isUserExist = True
            # store login in cookie session
            request.session["loginName"] = confirmedLoginName
            # display the primary account
            formSearchLogin = FormSearchLogin({"loginName": confirmedLoginName})
            userDict = getUserInfo(confirmedLoginName)
        #
        randomPassword = secrets.token_urlsafe(8).lower()
        formUserDetail = FormUserDetail(
            userDict
            | {"operator": request.session.get("operator")}
            | {"userPassword": randomPassword}
            | {"loginName": confirmedLoginName or loginName}
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
        formUserDetail = FormUserDetail(request.POST.dict())
        formUserDetail.fields["addressSelect"].choices = myChoices
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
                "address": postalAddress.get("Line1"),
                "city": postalAddress.get("City"),
                "state": postalAddress.get("ProvinceCode"),
                "country": "Canada",
                "postalCode": postalAddress.get("PostalCode"),
            }
            formUserDetail = FormUserDetail(request.POST.dict() | newAddress)

    """ --- """
    """ Button Pressed Create/UpdateUser """
    if request.method == "POST" and request.POST.get("updateUser"):
        initialUserDetail = FormUserDetail(request.POST.dict())
        if initialUserDetail.is_valid():
            submitToAladin(initialUserDetail.cleaned_data)
            # store login and operator in session cookie
            request.session["loginName"] = initialUserDetail.cleaned_data.get(
                "loginName"
            )
            request.session["operator"] = initialUserDetail.cleaned_data.get("operator")
            messages.add_message(
                request, messages.SUCCESS, f"User info has been submitted"
            )
            freezeForm = True
        else:
            messages.add_message(
                request,
                messages.WARNING,
                f"form still INVALID",
            )
        """
        # rebuilding form using POST + cleaned_data
        # .cleaned_data generated from is_valid call
        # .cleaned_data contains updated fields from validation such as ccexpiry
        # notice .cleaned_data does not contain fields wit errors, we need original POSTed data
        """
        formUserDetail = FormUserDetail(
            request.POST.dict() | initialUserDetail.cleaned_data
        )

    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "isDisabled": "disabled" if freezeForm else "",
        "isUserExist": isUserExist,
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formSearchLogin": formSearchLogin,
        "formUserDetail": formUserDetail,
    }
    return render(request, "updateuser/sample.html", context)
