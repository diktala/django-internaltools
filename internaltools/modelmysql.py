# -*- coding: utf-8 -*-
""" Model to access mysql

This contains functions to be called by python to access mysql
notice: may need to set env:
LC_ALL=en_US.UTF-8
LANG=en_US.UTF-8

Example:
#python:
import json
from modelmysql import queryDBall, queryDBrow, queryDBscalar
myResult = queryDBall('SELECT LoginName FROM UsersId')
myResultJson = json.dumps(myResult, indent = 4)
f = open('temp-file.json','w')
f.write(myResultJson)

>cat temp-file.json| jq -C '. | [.[]] | .[] | ."LoginName" '
"""
import os
import pymysql.cursors

MYSQL_IP = os.environ.get("MYSQL_IP")
MYSQL_USER = os.environ.get("MYSQL_USER")
MYSQL_PASS = os.environ.get("MYSQL_PASS")
MYSQL_NAME = os.environ.get("MYSQL_NAME")


def get_connection():
    dbLink = pymysql.connect(
        host=MYSQL_IP,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_NAME,
        cursorclass=pymysql.cursors.DictCursor,
    )
    return dbLink


def queryDBrow(query, params=dict()):
    dbLink = get_connection()
    with dbLink:
        with dbLink.cursor() as cursor:
            cursor.execute(query, params)
            queryResult = cursor.fetchone()
    return queryResult


def queryDBall(query, params=dict()):
    dbLink = get_connection()
    with dbLink:
        with dbLink.cursor() as cursor:
            cursor.execute(query, params)
            queryResult = cursor.fetchall()
    return queryResult


def queryDBscalar(query, params=dict()):
    scalar = ""
    result = queryDBrow(query, params)
    if isinstance(result, dict) and len(result) > 0:
        scalar = next(iter(result.values()))
    return scalar
