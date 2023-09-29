from django.test import TestCase
from django.urls import reverse
from .views import (
                FormSearchLogin,
                sanitizeLogin,
                countConfirmedLoginName,
                getLoginNameFromInvoiceNumber,
                getInvoiceNumberFromInvoiceString,
                getConfirmedLoginName,
                )

class SimpleTest(TestCase):

    def test_get_returns_200(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)


    def test_post_returns_200(self):
        response = self.client.post(reverse("index"))
        self.assertEqual(response.status_code, 200)


    def test_get_loginname(self):
        response = self.client.get(reverse("index"), {"loginName": "abc123"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")


    def test_form_validation_valid(self):
        formSearchLogin = FormSearchLogin( { "loginName": "sometest"} )
        self.assertTrue( formSearchLogin.is_valid() )


    def test_form_validation_invalid_capitalcase(self):
        formSearchLogin = FormSearchLogin( { "loginName": "someBADtest"} )
        self.assertFalse( formSearchLogin.is_valid() )


    def test_form_validation_invalid_bad_characters(self):
        formSearchLogin = FormSearchLogin( { "loginName": "some!@$%test"} )
        self.assertFalse( formSearchLogin.is_valid() )


    def test_sanitizeLogin(self):
        self.assertEqual( sanitizeLogin("name_is-ok."), "name_is-ok." )
        self.assertEqual( sanitizeLogin("name_is-NOT!@$-ok."), "" )


    def test_countConfirmedLoginName(self):
        self.assertEqual( countConfirmedLoginName("trial"), 1)
        self.assertEqual( countConfirmedLoginName("user_is_inexistant"), 0)


    def test_getLoginNameFromInvoiceNumber(self):
        self.assertEqual( getLoginNameFromInvoiceNumber("1000") , "ammina")
        self.assertEqual( getLoginNameFromInvoiceNumber("1001") , "patgar")

    def test_getInvoiceNumberFromInvoiceString(self):
        self.assertEqual( getInvoiceNumberFromInvoiceString('1000') , "1000")
        self.assertEqual( getInvoiceNumberFromInvoiceString(1234) , "1234")
        self.assertEqual( getInvoiceNumberFromInvoiceString('123.987654321') , "987654")

    def test_getConfirmedLoginName(self):
        self.assertEqual( getConfirmedLoginName('1000'), 'ammina')
        self.assertEqual( getConfirmedLoginName('1001'), 'patgar')
        self.assertEqual( getConfirmedLoginName('123.1001432'), 'patgar')
        self.assertEqual( getConfirmedLoginName('patgar'), 'patgar')
        self.assertEqual( getConfirmedLoginName('something555'), '')

