from datetime import datetime, timedelta
import re
from modelmssql import queryDBscalar


def getDateFormatted(initialDate=""):
    formattedDate = ""
    if isinstance(initialDate, datetime):
        formattedDate = initialDate.strftime("%Y-%m-%d")
    if isinstance(initialDate, str):
        formattedDate = re.sub(
            "([0-9]{4}).([0-9]{2}).([0-9]{2}).*", r"\1-\2-\3", initialDate
        )
    if not isDateValid(formattedDate):
        formattedDate = ""
    return formattedDate


def getNumberFormatted(initialNumber=""):
    try:
        return str("{:.2f}".format(float(initialNumber)))
    except ValueError:
        return ""


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
    lastDay = ""
    if isDateValid(dateToConvert):
        formattedDate = datetime.strptime(dateToConvert, "%Y-%m-%d")
        nextMonth = formattedDate.replace(day=28) + timedelta(days=5)
        lastDay = nextMonth - timedelta(days=nextMonth.day)
        lastDay = lastDay.strftime("%Y-%m-%d")
    return lastDay


def sanitizeLogin(loginName):
    loginSanitized = loginName if re.match(r"^[\w.-]{1,30}$", loginName) else ""
    return loginSanitized


def get_invoicenumber_from_obfuscated_number(invoiceString=""):
    invoiceNumber = "0"
    #
    if str(invoiceString).isdecimal() and len(str(invoiceString)) < 10:
        invoiceNumber = str(invoiceString)
    #
    matchResult = re.match("^[0-9]{3}\.([0-9]+)[0-9]{3}$", str(invoiceString))
    if matchResult:
        invoiceNumber = matchResult.group(1)
    #
    return invoiceNumber


def count_loginnames_in_database(loginToCheck):
    loginToCheckSanitized = sanitizeLogin(loginToCheck)
    loginFound = queryDBscalar(
        f"SELECT count(*) FROM UsersId where LoginName = lower('{loginToCheckSanitized}')"
    )
    return loginFound


def get_loginname_from_invoice(invoiceNumber):
    invoiceNumberSanitized = sanitizeLogin(invoiceNumber)
    invoiceNumberDigits = get_invoicenumber_from_obfuscated_number(
        invoiceNumberSanitized
    )
    loginName = queryDBscalar(
        f"SELECT LoginName FROM Invoices where InvoiceNumber = %s",
        str(invoiceNumberDigits),
    )
    if isinstance(loginName, str):
        return loginName.strip()
    else:
        return ""


def get_loginname_from_database(either_login_or_invoice=""):
    confirmedLoginName = ""
    if not isinstance(either_login_or_invoice, str):
        either_login_or_invoice = ""
    # case loginname is an invoicenumber
    invoiceNumber = either_login_or_invoice
    loginNameFromInvoice = get_loginname_from_invoice(invoiceNumber)
    loginFound = count_loginnames_in_database(loginNameFromInvoice)
    if str(loginFound) == "1":
        confirmedLoginName = loginNameFromInvoice
    # case loginname is normal alias
    loginName = either_login_or_invoice
    loginFound = count_loginnames_in_database(loginName)
    if str(loginFound) == "1":
        confirmedLoginName = loginName
    return confirmedLoginName
