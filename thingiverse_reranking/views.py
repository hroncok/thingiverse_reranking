from django.shortcuts import render
from django.conf import settings
from datetime import datetime
import thingiverse

KEY = settings.THINGIVERSE_KEY
SECRET = settings.THINGIVERSE_SECRET
TOKEN = settings.THINGIVERSE_TOKEN
DATE_FORMAT = '%Y-%m-%d'
DATE_LENGTH = 10

def index(request):
    '''The homepage'''
    t = thingiverse.Thingiverse({'client_id': KEY, 'client_secret': SECRET, 'redirect_uri': ''})
    t.connect(TOKEN)
    term = request.POST.get('term')
    if term:
        results = t.keyword_search(term)
        for result in results:
            # Get more info
            result['detail'] = t.get_thing(int(result['id']))

            # Calculate age
            added = datetime.strptime(result['detail']['added'][:DATE_LENGTH], DATE_FORMAT)
            delta = datetime.now() - added
            result['detail']['age'] = delta.days
    else:
        term = ""
        results = []
    return render(request, 'index.html', {'term': term, 'results': results, 'post': request.POST})
