from django.shortcuts import render


def index(request):
    '''The homepage'''
    return render(request, 'index.html', {})
