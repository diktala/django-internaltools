# -*- coding: utf-8 -*-
"""Fetch address from Canada Post

This module checks with Canada Post API and get a formatted Canadian Address
It requires an API code to work
'API_KEY1' : 'USED-FOR-SEARCHIN-POSTAL-CODES'
'API_KEY2' : 'USED-TO-FETCH-SPECIFIC-ID'
'API_REFERER' : 'https://www.example.com/some-example'

Example:
    python
    from . import getIDsFromIndex, getIndexFromPostal, getAddressFromID
    from pprint import pprint
    ->>> indexID = getIndexFromPostal('H1H 1H1')
    # 'CA|CP|ENG|1H1-H1H'
    #
    ->>> listOfAddresses = getIDsFromIndex(indexID)
    # { 'id': 'short desc', }
    #
    ->>> pprint(listOfAddresses)
    #
    ->>> detailAddress = getAddressFromID('CA|CP|B|1234567')
    # { 'Id': , 'Line1': , 'PostalCode': , 'ProvinceCode': , 'City': ,}
    #

Attributes:
    getIndexFromPostal('H1H 1H1'):
        returns String: ex: 'CA|CP|ENG|1H1-H1H'

    getIDsFromIndex('CA|CP|ENG|1H1-H1H'):
        returns DICT: { 'id': 'short desc', }

    getAddressFromID('CA|CP|B|1234567'):
        returns DICT: { 'Id': , 'Line1': , 'PostalCode': , 'ProvinceCode': , 'City': ,}

"""

import requests
import re
import os

API_KEY1 = os.environ.get("API_KEY1")
API_KEY2 = os.environ.get("API_KEY2")
API_REFERER = os.environ.get("API_REFERER")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; ) Gecko/20100101 Firefox/73.0",
    "Referer": API_REFERER,
}

payload = {
    "Key": API_KEY1,
    "Country": "CAN",
    "LanguagePreference": "fr",
    "SearchFor": "Everything",
    "OrderBy": "UserLocation",
    "$block": "true",
    "$cache": "true",
    "MaxResults": "500",
    "SearchTerm": "",
    "LastId": "",
}


def _sanitizeString(stringToCheck=""):
    stringReturned = ""
    if (
        isinstance(stringToCheck, str)
        and len(stringToCheck) < 60
        and re.match("^[a-zA-Z0-9 _|-]*$", stringToCheck)
    ):
        stringReturned = stringToCheck
    return stringReturned


def getIndexFromPostal(searchTerm="H0H 0H0"):
    searchTerm = _sanitizeString(searchTerm)
    payload["SearchTerm"] = searchTerm
    payload["LastId"] = ""
    url = "https://ws1.postescanada-canadapost.ca"
    url += "/AddressComplete/Interactive/Find/v2.10/json3ex.ws"
    indexID = ""
    try:
        r = requests.get(url, headers=headers, params=payload)
        indexID = r.json()[list(r.json().keys())[0]][0]["Id"]
    except:
        pass

    return indexID


def getIDsFromIndex(Index=""):
    Index = _sanitizeString(Index)
    payload["SearchTerm"] = ""
    payload["LastId"] = Index
    url = "https://ws1.postescanada-canadapost.ca"
    url += "/AddressComplete/Interactive/Find/v2.10/json3ex.ws"
    listOfAddresses = {}
    try:
        s = requests.get(url, headers=headers, params=payload)
        for eachID in s.json()[list(s.json().keys())[0]]:
            listOfAddresses[eachID["Id"]] = (
                eachID["Text"] + ", " + eachID["Description"]
            )
    except:
        pass

    return listOfAddresses


def getAddressFromID(addressID=""):
    addressID = _sanitizeString(addressID)
    payload = {"Key": API_KEY2, "Source": "", "$cache": "true", "Id": addressID}
    url = "https://ws1.postescanada-canadapost.ca"
    url += "/AddressComplete/Interactive/RetrieveFormatted/v2.10/json3ex.ws"
    detailAddress = {}

    try:
        t = requests.get(url, headers=headers, params=payload)
        detailAddress["Id"] = addressID
        detailAddress["Line1"] = t.json()["Items"][0]["Line1"]
        detailAddress["PostalCode"] = t.json()["Items"][0]["PostalCode"]
        detailAddress["ProvinceCode"] = t.json()["Items"][0]["ProvinceCode"]
        detailAddress["City"] = t.json()["Items"][0]["City"]
    except:
        pass

    return detailAddress
