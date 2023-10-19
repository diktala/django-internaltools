# -*- coding: utf-8 -*-
""" access moneris CC processor

Example:
#python:
import moneris

creditCard = {"Num": "4111111111111111",
              "ExpMonth": "12",
              "ExpYear": "20",
              "Amount": "0.01"}
payment = moneris.pay(creditCard)

"""

import os
import re
import requests
from time import time


def convertToFloat(valueToConvert):
    try:
        result = float(valueToConvert)
    except (ValueError, TypeError):
        result = float(0)
    return result


def getPageFolder(amount):
    result = "purchase"
    if convertToFloat(amount) < 0:
        result = "indrefund"
    return result


def extractFromHtml(pattern, monerisPage):
    match = ""
    if re.match(pattern, monerisPage, flags=re.DOTALL):
        match = re.sub(pattern, r"\1", monerisPage, flags=re.DOTALL)
        match = re.sub("<[^<]+?>", "", match)
    return match


username = os.environ.get("MONERIS_USERNAME")
storeid = os.environ.get("MONERIS_STOREID")
password = os.environ.get("MONERIS_PASSWORD")
reset_answer = os.environ.get("MONERIS_RESET_ANSWER")
USERAGENT = "Mozilla/4.0"
REFERER = "https://www3.moneris.com/mpg/index.php"
headers = {"User-Agent": USERAGENT, "referer": REFERER}
url_login = "https://www3.moneris.com/mpg/index.php"


def getSession():
    # start a session to store cookies
    session = requests.Session()
    return session


def getCSRF(session):
    # get CSRF
    url = url_login
    data = dict()
    field = dict()
    r = session.get(url, headers=headers, data=data)
    monerisPage = r.text
    regex = r'.*input type="text" class="textbox" name="([^"]+).*input type="text" class="textbox" name="([^"]+).*input type="password" class="textbox" name="([^"]+).*'
    match = re.sub(regex, r"\1;\2;\3", monerisPage, flags=re.DOTALL)
    (field["User"], field["Store"], field["Password"]) = match.split(";")
    return field


def loginPortal(session, csrfField):
    # Login
    url = url_login
    data = {
        "attempt": "",
        csrfField.get("User"): username,
        csrfField.get("Store"): storeid,
        csrfField.get("Password"): password,
        "do_login": "Submit",
    }
    # print (f"DEBUG: url: {url}")
    # print (f"DEBUG: headers: {headers}")
    # print (f"DEBUG: data: {data}")
    r = session.post(url, headers=headers, data=data)
    monerisPage = r.text
    return monerisPage


def loginConfirmPortal(session):
    # Login2
    url = url_login
    data = {
        "qid": "9",
        "dqid": "3",
        "reset_answer": reset_answer,
        "doQuestionVerification": "true",
        "verifyQuestion": "Submit",
    }
    # print (f"DEBUG: url: {url}")
    # print (f"DEBUG: headers: {headers}")
    # print (f"DEBUG: data: {data}")
    r = session.post(url, headers=headers, data=data)
    monerisPage = r.text
    return monerisPage


def submitPayment(session, creditCard):
    # make payment
    cc_amount = creditCard.get("Amount")
    amount = convertToFloat(cc_amount)
    absoluteAmount = abs(amount)
    pageFolder = getPageFolder(amount)
    orderid = str(int(time()))
    url_pay = f"https://www3.moneris.com/mpg/terminal/{pageFolder}/index.php"
    url = url_pay
    data = {
        "payment_method": "moto",
        "order_no": orderid,
        "cust_id": "my_customer",
        "amount": absoluteAmount,
        "cc_number": creditCard.get("Num"),
        "exp_month": creditCard.get("ExpMonth"),
        "exp_year": creditCard.get("ExpYear"),
        "crypt_type": "0",
        "process": "Process+Transaction",
    }
    # print (f"DEBUG: url: {url}")
    # print (f"DEBUG: headers: {headers}")
    # print (f"DEBUG: data: {data}")
    r = session.post(url, headers=headers, data=data)
    monerisPage = r.text
    return monerisPage


def pay(creditCard):
    """
    creditCard = {
        "Num": "4111111111111111",
        "ExpMonth": "12",
        "ExpYear": "22",
        "Amount": "0.01",
    }
    """
    session = getSession()
    csrfField = getCSRF(session)
    monerisPage = loginPortal(session, csrfField)
    monerisPage = loginConfirmPortal(session)
    monerisPage = submitPayment(session, creditCard)

    payment = dict()
    payment["result"] = extractFromHtml(r".*Result:.*?<b> *(.*)<.b>.*", monerisPage)
    payment["orderid"] = extractFromHtml(
        r".*Order ID:.*?<td[^>]*> *(.*?)<.td>.*", monerisPage
    )
    payment["reference"] = extractFromHtml(
        r".*Reference Number:.*?<td[^>]*> *(.*?)<.td>.*", monerisPage
    )
    payment["authorization"] = extractFromHtml(
        r".*Authorization Code:.*?<td[^>]*> *(.*?)<.td>.*", monerisPage
    )
    payment["response"] = extractFromHtml(
        r".*Response Code:.*?<td[^>]*> *(.*?)<.td>.*", monerisPage
    )
    payment["message"] = extractFromHtml(
        r".*Message:.*?<td[^>]*> *(.*?)<.td>.*", monerisPage
    )
    payment["transactionTime"] = extractFromHtml(
        r".*Transaction Time:.*?<td[^>]*> *(.*?)<.td>.*", monerisPage
    )
    payment["transactionDate"] = extractFromHtml(
        r".*Transaction Date:.*?<td[^>]*> *(.*?)<.td>.*", monerisPage
    )
    payment["transactionType"] = extractFromHtml(
        r".*Transaction Type:.*?<td[^>]*> *(.*?)<.td>.*", monerisPage
    )
    payment["amount"] = extractFromHtml(
        r".*Amount:.*?<td[^>]*> *(.*?)<.td>.*", monerisPage
    )

    return payment
