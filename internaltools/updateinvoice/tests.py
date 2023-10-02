from django.test import TestCase
from django.urls import reverse
import commons


class SimpleTest(TestCase):

    def test_get_returns_200(self):
        response = self.client.get(reverse("updateinvoice:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Update Invoice")


    def test_post_returns_200(self):
        response = self.client.post(reverse("updateinvoice:index"))
        self.assertEqual(response.status_code, 200)


    def test_get_loginName(self):
        response = self.client.get(reverse("updateinvoice:index"), {"loginName": "test"} )
        self.assertEqual(response.status_code, 200)


"""
    def test_form_validation_valid(self):
        formSearchLogin = FormSearchLogin( { "loginName": "sometest"} )
        self.assertTrue( formSearchLogin.is_valid() )

    def test_form_validation_invalid_capitalcase(self):
        formSearchLogin = FormSearchLogin( { "loginName": "someBADtest"} )
        self.assertFalse( formSearchLogin.is_valid() )

    def test_form_validation_invalid_bad_characters(self):
        formSearchLogin = FormSearchLogin( { "loginName": "some!@$%test"} )
        self.assertFalse( formSearchLogin.is_valid() )

    def test_countConfirmedLoginName(self):
        self.assertEqual( countConfirmedLoginName("trial"), 1)
        self.assertEqual( countConfirmedLoginName("user_is_inexistant"), 0)

    def test_getLoginNameFromInvoiceNumber(self):
        self.assertEqual( getLoginNameFromInvoiceNumber("1000") , "ammina")
        self.assertEqual( getLoginNameFromInvoiceNumber("1001") , "patgar")

    def test_getConfirmedLoginName(self):
        self.assertEqual( getConfirmedLoginName('1000'), 'ammina')
        self.assertEqual( getConfirmedLoginName('1001'), 'patgar')
        self.assertEqual( getConfirmedLoginName('123.1001432'), 'patgar')
        self.assertEqual( getConfirmedLoginName('patgar'), 'patgar')
        self.assertEqual( getConfirmedLoginName('something555'), '')
"""

"""

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
                regex="^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
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
                regex="^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
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
                regex="^[\w. &'<>;+$()/=@,:*#\"\\[\]-]*$"
                message="invalid characters",
            )
        ],
    )
    invoiceStatus = forms.CharField(
        label="Invoice Status",
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
                regex="^(Printed)|(Reported)|(Paid)|(Canceled)$"
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
        min_length=1,
        max_length=20,
        validators=[
            RegexValidator(
                regex="^[-]?[0-9.]+$"
                message="invalid characters",
            )
        ],
    )
"""
