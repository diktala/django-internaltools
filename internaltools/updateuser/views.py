from django.shortcuts import render
from django.http import HttpResponse
# from .models import UsersId
from modelmssql import queryDBall, queryDBrow, queryDBscalar

def index(request):
    # example query using django models
    # myResult = UsersId.objects.using('db2')
    # myResultList = (myResult.values()[0]['LoginName'])

    # example query using modelmssql
    myMssqlResult = queryDBall('SELECT * FROM Taxes')
    myMssqlResultSingle = myMssqlResult[0]['Tax1']
    context = {'test': '123 test'}
    # return HttpResponse(f"Hello, the Tax1 is {myMssqlResultSingle}")
    return render(request, 'updateuser/sample.html', context)
