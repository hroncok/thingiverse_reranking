from django.shortcuts import render
from django.conf import settings
import thingiverse


KEY = settings.THINGIVERSE_KEY
SECRET = settings.THINGIVERSE_SECRET
TOKEN = settings.THINGIVERSE_TOKEN


def index(request):
    '''The homepage'''
    t = thingiverse.Thingiverse({'client_id': KEY, 'client_secret': SECRET, 'redirect_uri': ''})
    t.connect(TOKEN)
    term = request.GET.get('term')
    if term:
        results = t.keyword_search(term)
    else:
        term = ""
        results = []
    return render(request, 'index.html', {'term': term, 'results': results})
