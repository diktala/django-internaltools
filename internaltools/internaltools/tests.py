from django.test import TestCase
from django.urls import reverse
import commons


class SimpleTest(TestCase):

    def test_getDateFormatted(self):
        self.assertEqual( commons.getDateFormatted("2023-01-01"), "2023-01-01" )
        self.assertEqual( commons.getDateFormatted("2023-01-01blabla"), "2023-01-01" )
        self.assertEqual( commons.getDateFormatted("2023.01.01blabla"), "2023-01-01" )
        self.assertEqual( commons.getDateFormatted("2023.91.01"), "" )
        self.assertEqual( commons.getDateFormatted("some bad data"), "" )


    def test_isDateValid(self):
        self.assertTrue( commons.isDateValid("2023-01-01") )
        self.assertFalse( commons.isDateValid("some bad data") )


    def test_isDateExpired(self):
        self.assertTrue( commons.isDateExpired("1930-01-01") )
        self.assertFalse( commons.isDateExpired("2222-01-01") )
        self.assertFalse( commons.isDateExpired("BUGBUG") )


    def test_getLastDay(self):
        self.assertEqual( commons.getLastDay('2023-01-01'), '2023-01-31' )
        self.assertEqual( commons.getLastDay('2023-01-31'), '2023-01-31' )
        self.assertEqual( commons.getLastDay('BUGBUG'), '' )


    def test_sanitizeLogin(self):
        # re.match(r"^[\w.-]{1,30}$"
        self.assertEqual( commons.sanitizeLogin('CAPS-Lower123.'), 'CAPS-Lower123.')
        self.assertEqual( commons.sanitizeLogin('badHAS Space'), '' )
        self.assertEqual( commons.sanitizeLogin('badHAS:!@#$%^&*'), '' )
        self.assertEqual( commons.sanitizeLogin('badTooLongSentenceBeyond30chars'), '' )


    def test_get_invoicenumber_from_obfuscated_number(self):
        # re.match("^[0-9]{3}.([0-9]+)[0-9]{3}$"
        self.assertEqual( commons.get_invoicenumber_from_obfuscated_number('999.12345999'), '12345')
        self.assertEqual( commons.get_invoicenumber_from_obfuscated_number('12345'), '12345')
        self.assertEqual( commons.get_invoicenumber_from_obfuscated_number('BUGBUG'), '0')
        self.assertEqual( commons.get_invoicenumber_from_obfuscated_number(''), '0')
        self.assertEqual( commons.get_invoicenumber_from_obfuscated_number('123.345'), '0')
        self.assertEqual( commons.get_invoicenumber_from_obfuscated_number('01234567890123'), '0')


    def test_count_loginnames_in_database(self):
        self.assertEqual( commons.count_loginnames_in_database("trial"), 1)
        self.assertEqual( commons.count_loginnames_in_database("user_is_inexistant"), 0)


    def test_get_loginname_from_invoice(self):
        self.assertEqual( commons.get_loginname_from_invoice("1000"), "ammina")
        self.assertEqual( commons.get_loginname_from_invoice("123.1000123"), "ammina")


    def test_get_loginname_from_database(self):
        self.assertEqual( commons.get_loginname_from_database("trial"), "trial")
        self.assertEqual( commons.get_loginname_from_database("1000"), "ammina")
        self.assertEqual( commons.get_loginname_from_database("123.1000123"), "ammina")
        self.assertEqual( commons.get_loginname_from_database("user_is_inexistant"), "")
        self.assertEqual( commons.get_loginname_from_database("user_#$_inexistant"), "")
        self.assertEqual( commons.get_loginname_from_database("TRial"), "TRial")
        self.assertEqual( commons.get_loginname_from_database(""), "")
        self.assertEqual( commons.get_loginname_from_database(1000), "")
        self.assertEqual( commons.get_loginname_from_database(None), "")
        self.assertEqual( commons.get_loginname_from_database("has spaces"), "")


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
    """

