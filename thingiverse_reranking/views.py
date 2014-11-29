from django.shortcuts import render
from django.conf import settings
from datetime import datetime
from Levenshtein import distance
import thingiverse


KEY = settings.THINGIVERSE_KEY
SECRET = settings.THINGIVERSE_SECRET
TOKEN = settings.THINGIVERSE_TOKEN
DATE_FORMAT = '%Y-%m-%d'
DATE_LENGTH = 10
FEATURES = ['name', 'creator', 'like_count', 'collect_count', 'age']
STRINGS = ['name', 'creator']


def normalize(value, maximum, weight):
    '''Normalizes the given value to <0,weight>'''
    if maximum == 0:
        return 0
    else:
        return float(value) / maximum * weight


def index(request):
    '''The homepage'''
    t = thingiverse.Thingiverse({'client_id': KEY, 'client_secret': SECRET, 'redirect_uri': ''})
    t.connect(TOKEN)
    term = request.POST.get('term')
    if term:
        results = t.keyword_search(term)

        maxs = {}
        normalized = {}
        weights = {}

        for feature in FEATURES:
            value = request.POST.get(feature)
            if value:
                if feature in STRINGS:
                    value = 0
                else:
                    value = int(value)
                maxs[feature] = value
                weight = request.POST.get(feature + '_weight')
                if weight:
                    weights[feature] = int(weight)
                else:
                    weights[feature] = 1

        for result in results:
            # Get more info
            result['detail'] = t.get_thing(int(result['id']))

            # Calculate age
            added = datetime.strptime(result['detail']['added'][:DATE_LENGTH], DATE_FORMAT)
            delta = datetime.now() - added
            result['detail']['age'] = delta.days

            result['absolute'] = {}
            result['relative'] = {}

            # Calculate numeric constrains
            for feature in maxs:
                # This should really use "in STRINGS", but creator name and thing name are differently saved in the dict
                if feature == 'creator':
                    result['absolute'][feature] = distance(result[feature]['name'], request.POST.get(feature))
                elif feature == 'name':
                    result['absolute'][feature] = distance(result[feature], request.POST.get(feature))
                else:
                    result['absolute'][feature] = abs(int(result['detail'][feature])-int(request.POST.get(feature)))

                # Store maxs
                maxs[feature] = max(maxs[feature], result['absolute'][feature])

        # Normalize calculated values
        for result in results:
            result['penalty'] = 0.0
            for feature in maxs:
                result['relative'][feature] = normalize(result['absolute'][feature], maxs[feature], weights[feature])
                result['penalty'] += result['relative'][feature]
        results = sorted(results, key=lambda k: k['penalty'])
    else:
        term = ""
        results = []
    return render(request, 'index.html', {'term': term, 'results': results, 'post': request.POST})
