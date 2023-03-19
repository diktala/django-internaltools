import os
from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.core.validators import RegexValidator
import re
from modelmssql import queryDBall, queryDBrow, queryDBscalar

class FormSearchLogin(forms.Form):
    loginName = forms.CharField(
        label='Login Name',
        widget=forms.TextInput(attrs={
            'placeholder': 'Customer username ...',
            'class': 'form-control',
        }),
        required=True,
        min_length=1,
        max_length=20,
        validators=[
            RegexValidator(
                regex='^[a-z0-9][a-z0-9.-]*$',
                message='invalid characters',
                flags=re.IGNORECASE,
            )
        ],
    )

class FormUserDetail(forms.Form):
    loginName = forms.CharField(
        disabled=True,
    )
    firstName = forms.CharField(
        label='First Name',
        widget=forms.TextInput(attrs={
            'placeholder': ' ...',
            'class': 'form-control',
        }),
        required=True,
        min_length=1,
        max_length=30,
        validators=[
            RegexValidator(
                regex="^[\w. &'-]*[\w]$",
                message='invalid characters',
            )
        ],
    )
    lastName = forms.CharField(
        label='Last Name',
        widget=forms.TextInput(attrs={
            'placeholder': ' ...',
            'class': 'form-control',
        }),
        required=True,
        min_length=1,
        max_length=30,
        validators=[
            RegexValidator(
                regex="^[\w. &'-]*[\w]$",
                message='invalid characters',
            )
        ],
    )


def index(request):
    defaultData = {'loginName': '',}
    formSearchLogin = FormSearchLogin(defaultData)
    formUserDetail = FormUserDetail(defaultData)

    if request.GET.get("loginName"):
        print (F"DEBUG MESSAGE: method GET {request.GET.get('loginName')} ")
        formSearchLogin = FormSearchLogin(request.GET)

    if request.method == 'POST':
        print ('DEBUG MESSAGE: method POST')
        formUserDetail = FormUserDetail(request.POST)
        if formSearchLogin.is_valid():
            print ('DEBUG MESSAGE: form is valid')
            # return HttpResponse('thanks')
        else:
            print ('DEBUG MESSAGE: form is NOT valid')
            # return HttpResponse('form is invalid')

    # example query using django models
    # add this: from .models import UsersId
    # myResult = UsersId.objects.using('db2')
    # myResultList = (myResult.values()[0]['LoginName'])

    # example query using modelmssql
    myMssqlResult = queryDBall('SELECT * FROM Taxes')
    myMssqlResultSingle = myMssqlResult[0]['Tax1']

    DOMAIN = os.environ.get("DOMAIN")
    loginName = 'test123'
    urlQuery = f"LoginName={loginName}"
    context = {'test': '123 test',
               'myTax': myMssqlResultSingle,
               'domain': DOMAIN,
               'urlQuery': urlQuery,
               'formSearchLogin': formSearchLogin,
               'formUserDetail': formUserDetail,
    }
    # return HttpResponse(f"Hello, the Tax1 is {myMssqlResultSingle}")
    return render(request, 'updateuser/sample.html', context)
