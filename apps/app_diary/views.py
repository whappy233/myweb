from django.shortcuts import render

from .models import Diary


def aszx(request):
    diaries = Diary.objects.all()
    return render(request, 'tp/日记.html', {'diaries': diaries})


def details(request):
    return render(request, 'tp/日记.html')
