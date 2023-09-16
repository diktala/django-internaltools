import os
from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re
from modelmssql import queryDBall, queryDBrow, queryDBscalar


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
                regex="^[a-z0-9][a-z0-9.-]*$",
                message="invalid characters",
                flags=re.IGNORECASE,
            )
        ],
    )


class FormUserDetail(forms.Form):
    loginName = forms.CharField(
        widget=forms.HiddenInput(),
        disabled=True,
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
        max_length=30,
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
        max_length=30,
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
        max_length=30,
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
                regex="^[\w. &'-]*[\w.]$",
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
        max_length=30,
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
        max_length=30,
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
        max_length=30,
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
            ("", "<<< Lookup"),
        ],
        initial="",
        widget=forms.Select(
            attrs={
                "class": "form-control",
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
        max_length=30,
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
        max_length=30,
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
                "class": "form-control",
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
    paymentMethod = forms.CharField(
        label="Payment Method",
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
        max_length=30,
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
        max_length=30,
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
        max_length=30,
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
        max_length=30,
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
        max_length=30,
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
        max_length=30,
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
        max_length=30,
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
                "class": "form-control",
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
        max_length=30,
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
                regex="^[\w. &'-]*[\w.]$",
                message="invalid characters",
            )
        ],
    )
    dateJoined = forms.CharField(
        label="Date Joined",
        widget=forms.HiddenInput(),
        disabled=True,
        min_length=1,
        max_length=30,
        validators=[
            RegexValidator(
                regex="^[0-9]{4}-[0-9]{2}-[0-9]{2}( 00:00:00)?$",
                message="incorrect characters used 2000-01-01",
            )
        ],
    )
    def clean_lastName(self):
        data = self.cleaned_data["lastName"]
        if "some-word" not in data:
            raise ValidationError("You have forgotten about some-word!")
        return data

    def clean(self):
        cleaned_data = super().clean()
        firstName = cleaned_data.get("firstName")
        lastName = cleaned_data.get("lastName")
        if firstName and lastName and "help" not in firstName:
                msg = "Must put 'help' in login"
                self.add_error("firstName", msg)

def sanitizeLogin(loginName):
    loginSanitized = loginName if re.match(r"[\w.-]{1,30}", loginName) else ""
    return loginSanitized

def getConfirmedLoginName(loginToCheck):
    loginToCheckSanitized = sanitizeLogin(loginToCheck)
    myMssqlResult = queryDBscalar(f"SELECT LoginName FROM UsersId where LoginName = '{loginToCheckSanitized}'")
    return myMssqlResult

def index(request):
    defaultData = {
        "loginName": "",
    }
    formSearchLogin = FormSearchLogin(defaultData)
    formUserDetail = FormUserDetail()

    isUserExist = False
    if request.GET.get("loginName"):
        print(f"DEBUG MESSAGE: method GET {request.GET.get('loginName')} ")
        formSearchLogin = FormSearchLogin(request.GET)
        if formSearchLogin.is_valid():
            print("DEBUG MESSAGE: form is valid")
            loginName = request.GET.get("loginName")
            print(f"DEBUG MESSAGE: checking if login {loginName} is found")
            loginChecked = getConfirmedLoginName(loginName)
            print(f"DEBUG MESSAGE: after checking, the loginName = {loginChecked}")
            isUserExist = True if ( request.GET.get('loginName') == loginChecked ) else False


    if request.method == "POST":
        print("DEBUG MESSAGE: method POST")
        formUserDetail = FormUserDetail(request.POST)
        if formSearchLogin.is_valid():
            print("DEBUG MESSAGE: form is valid")
            # return HttpResponse('thanks')
        else:
            print("DEBUG MESSAGE: form is NOT valid")
            # return HttpResponse('form is invalid')

    # example query using django models
    # add this: from .models import UsersId
    # myResult = UsersId.objects.using('db2')
    # myResultList = (myResult.values()[0]['LoginName'])

    # example query using modelmssql
    myMssqlResult = queryDBall("SELECT * FROM Taxes")
    myMssqlResultSingle = myMssqlResult[0]["Tax1"]

    loginName = request.GET.get('loginName')
    urlQuery = f"LoginName={loginName}"
    context = {
        "loginName": loginName,
        "buttonStyle": "success" if isUserExist else "secondary",
        "isValid": "isValid" if isUserExist else "is-invalid",
        "isDisabled": "" if isUserExist else "disabled",
        "myTax": myMssqlResultSingle,
        "domain": os.environ.get("DOMAIN"),
        "urlQuery": urlQuery,
        "formSearchLogin": formSearchLogin,
        "formUserDetail": formUserDetail,
    }
    # return HttpResponse(f"Hello, the Tax1 is {myMssqlResultSingle}")
    return render(request, "updateuser/sample.html", context)
