from django.shortcuts import render


def test_500(request):
    raise Exception('test!')


def index(request):
    return render(request, 'index.html')
