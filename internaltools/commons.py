from datetime import datetime, timedelta
import re


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


def getInvoiceNumberFromInvoiceString(invoiceString=""):
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
