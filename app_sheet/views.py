from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def index(request):
    return render(request, 'app_sheet/xx.html')
    # return HttpResponse('sqwdwed')

def updata(request):
    print(10*'*')
    return HttpResponse('fff')