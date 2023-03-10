import os
from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.core.validators import RegexValidator
from modelmssql import queryDBall, queryDBrow, queryDBscalar

class SearchLoginForm(forms.Form):
    loginName = forms.CharField(
        label='Login Name',
        max_length=16,
        widget=forms.TextInput(attrs={
            'placeholder': 'enter login name ...',
            'class': 'form-control',
        }),
        validators=[RegexValidator('^[0-9]+$', message='only numbers are allowed')],
    )

def index(request):
    if request.method == 'POST':
        print ('DEBUG MESSAGE: method POST')
        form = SearchLoginForm(request.POST)
        if form.is_valid():
            print ('DEBUG MESSAGE: form is valid')
            # return HttpResponse('thanks')
        else:
            print ('DEBUG MESSAGE: form is NOT valid')
            # return HttpResponse('form is invalid')
    else:
        defaultData = {'loginName': 'some default id',}
        form = SearchLoginForm(defaultData)

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
               'form': form,
    }
    # return HttpResponse(f"Hello, the Tax1 is {myMssqlResultSingle}")
    return render(request, 'updateuser/sample.html', context)
