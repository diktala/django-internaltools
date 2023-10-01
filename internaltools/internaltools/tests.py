from django.test import TestCase
from django.urls import reverse
from commons import isDateValid, isDateExpired, getLastDay, sanitizeLogin, getInvoiceNumberFromInvoiceString


class SimpleTest(TestCase):

    def test_isDateValid(self):
        self.assertTrue( isDateValid("2023-01-01") )
        self.assertFalse( isDateValid("some bad data") )


    def test_isDateExpired(self):
        self.assertTrue( isDateExpired("1930-01-01") )
        self.assertFalse( isDateExpired("2222-01-01") )
        self.assertFalse( isDateExpired("BUGBUG") )


    def test_getLastDay(self):
        self.assertEqual( getLastDay('2023-01-01'), '2023-01-31' )
        self.assertEqual( getLastDay('2023-01-31'), '2023-01-31' )
        self.assertEqual( getLastDay('BUGBUG'), '' )


    def test_sanitizeLogin(self):
        # re.match(r"^[\w.-]{1,30}$"
        self.assertEqual( sanitizeLogin('CAPS-Lower123.'), 'CAPS-Lower123.')
        self.assertEqual( sanitizeLogin('badHAS Space'), '' )
        self.assertEqual( sanitizeLogin('badHAS:!@#$%^&*'), '' )
        self.assertEqual( sanitizeLogin('badTooLongSentenceBeyond30chars'), '' )


    def test_getInvoiceNumberFromInvoiceString(self):
        # re.match("^[0-9]{3}.([0-9]+)[0-9]{3}$"
        self.assertEqual( getInvoiceNumberFromInvoiceString('999.12345999'), '12345')
        self.assertEqual( getInvoiceNumberFromInvoiceString('12345'), '12345')
        self.assertEqual( getInvoiceNumberFromInvoiceString('BUGBUG'), '0')
        self.assertEqual( getInvoiceNumberFromInvoiceString(''), '0')
        self.assertEqual( getInvoiceNumberFromInvoiceString('123.345'), '0')
        self.assertEqual( getInvoiceNumberFromInvoiceString('01234567890123'), '0')

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
