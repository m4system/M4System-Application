from django.shortcuts import render


# Create your views here.

def index(request, plugin):
    context = {'name': 'index'}
    return render(request, 'default/default_string.html', context)


def dashboard(request, plugin):
    context = {'name': 'dashboard'}
    return render(request, 'default_string.html', context)
