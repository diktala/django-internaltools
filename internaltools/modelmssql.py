# -*- coding: utf-8 -*-
""" Model to access Aladin mssql

This contains functions to be called by python to access Aladin sql
notice: may need to set env:
LC_ALL=en_US.UTF-8
LANG=en_US.UTF-8

Example:
#python:
import json
from modelmssql import queryDBall, queryDBrow, queryDBscalar
myResult = queryDBall('SELECT LoginName FROM UsersId')
myResultJson = json.dumps(myResult, indent = 4)
f = open('temp-file.json','w')
f.write(myResultJson)

>cat temp-file.json| jq -C '. | [.[]] | .[] | ."LoginName" '
"""
import os
from pymssql import _mssql

DB_IP = os.environ.get("DB_IP")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")


class fake_mssql:
    def connect(server, user, password, database):
        return fake_mssql()

    def execute_query(self, query, params):
        return fake_mssql()

    def execute_scalar(self, query, params):
        return fake_mssql()

    def close(self):
        return fake_mssql()


if DB_IP:
    dbLink = _mssql.connect(
        server=DB_IP,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
    )
else:
    dbLink = fake_mssql.connect(
        server="",
        user="",
        password="",
        database="",
    )


def queryDBrow(query, params=""):
    dbLink.execute_query(query, params)
    queryResult = {}
    # trick to differentiate pymssql vs fake_mssql
    if hasattr(dbLink, "__iter__"):
        for row in dbLink:
            for column in row.keys():
                if isinstance(column, str):
                    queryResult.update({column: row[column]})
            break
    dbLink.close
    return queryResult


def queryDBscalar(query, params=""):
    queryResult = dbLink.execute_scalar(query, params)
    dbLink.close
    return queryResult


def queryDBall(query, params=""):
    dbLink.execute_query(query, params)
    # lineNumber = 0
    allRows = []
    rowResult = {}
    for row in dbLink:
        for column in row.keys():
            if isinstance(column, str):
                rowResult.update({column: row[column]})
        # allRows[lineNumber] = rowResult.copy()
        # allRows[lineNumber] = rowResult.copy()
        # lineNumber += 1
        allRows.append(rowResult.copy())
    dbLink.close
    return allRows
