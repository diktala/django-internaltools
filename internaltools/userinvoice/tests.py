from django.test import TestCase
from django.urls import reverse
from .views import (
                FormSearchLogin,
                )

class SimpleTest(TestCase):

    def test_get_returns_200(self):
        response = self.client.get(reverse("userinvoice:index"))
        self.assertEqual(response.status_code, 200)


    def test_post_returns_200(self):
        response = self.client.post(reverse("userinvoice:index"))
        self.assertEqual(response.status_code, 200)


    def test_get_loginname(self):
        response = self.client.get(reverse("userinvoice:index"), {"loginName": "abc123"})
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


