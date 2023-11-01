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
    loginName = ""
    if len(invoiceNumberDigits) > 0:
        loginName = queryDBscalar(
            f"SELECT LoginName FROM Invoices where InvoiceNumber = %s",
            str(invoiceNumberDigits),
        )
    if isinstance(loginName, str):
        return loginName.strip()
    else:
        return ""


def get_loginname_from_secondary_mail(secondaryMail):
    secondaryMailSanitized = sanitizeLogin(secondaryMail)
    loginName = ""
    if len(secondaryMailSanitized) > 0:
        loginName = queryDBscalar(
            f"SELECT MainLoginName FROM SecondaryMailbox where MailBox = %s",
            str(secondaryMailSanitized),
        )
    if isinstance(loginName, str):
        return loginName.strip()
    else:
        return ""


def get_loginname_from_database(either_login_or_invoice=""):
    confirmedLoginName = ""
    if not isinstance(either_login_or_invoice, str):
        either_login_or_invoice = ""
    #
    # case loginname is a secondary mail account
    main_login = get_loginname_from_secondary_mail(either_login_or_invoice)
    loginFound = count_loginnames_in_database(main_login)
    if str(loginFound) == "1":
        confirmedLoginName = main_login
    #
    # case loginname is an invoicenumber
    invoiceNumber = either_login_or_invoice
    loginNameFromInvoice = get_loginname_from_invoice(invoiceNumber)
    loginFound = count_loginnames_in_database(loginNameFromInvoice)
    if str(loginFound) == "1":
        confirmedLoginName = loginNameFromInvoice
    #
    # case loginname is normal alias
    loginName = either_login_or_invoice
    loginFound = count_loginnames_in_database(loginName)
    if str(loginFound) == "1":
        confirmedLoginName = loginName
    #
    return confirmedLoginName


def simpleCrypt(varToCrypt=""):
    simpleCrypt = ""
    for i in range(len(varToCrypt) - 1, -1, -1):
        simpleCrypt = simpleCrypt + chr(ord(varToCrypt[i]) ^ 22)
    return simpleCrypt


# hack to store operators and other messages in user rasuser
def get_tag_from_database(tag=""):
    # example: tag = "OPERATORS:"
    sql_query = f"""
        SET ROWCOUNT 1;
        SELECT Desc1
        FROM TransactionHistory
        WHERE LoginName = 'rasuser' AND Desc1 like %(tag)s + '%'
        ORDER BY TranDate DESC;
        set ROWCOUNT 0;
        """
    sql_param = {
        "tag": tag,
    }
    result = queryDBscalar(sql_query, sql_param)
    # sanity check
    output = "not-found"
    if isinstance(result, str):
        match = re.search(f"^{tag}(.+)$", result)
        if match:
            output = match[1].strip()
    return output


def get_operators():
    result = get_tag_from_database("OPERATORS:")
    # sanity check
    output = "not-found"
    if isinstance(result, str):
        match = re.search(f"^[A-Za-z- ]+$", result)
        if match:
            output = result.strip()
    return output


def get_standard_email():
    MSGFR = get_tag_from_database("MSGFR:")
    MSGEN = get_tag_from_database("MSGEN:")
    MSGEND = get_tag_from_database("MSGEND:")
    MSGNAME = get_tag_from_database("MSGNAME:")
    MSGEMAIL = get_tag_from_database("MSGEMAIL:")
    MSGSUBJECT = get_tag_from_database("MSGSUBJECT:")

    output = dict()
    output["MSGFR"] = re.sub("#", r"\n", MSGFR)
    output["MSGEN"] = re.sub("#", r"\n", MSGEN)
    output["MSGEND"] = re.sub("#", r"\n", MSGEND)
    output["MSGNAME"] = MSGNAME
    output["MSGEMAIL"] = MSGEMAIL
    output["MSGSUBJECT"] = MSGSUBJECT
    return output
