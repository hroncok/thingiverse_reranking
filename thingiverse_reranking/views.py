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


def normalize(value, total, weight):
    '''Normalizes the given value, so all in total equals to weight'''
    if total:
        return float(value) / total * weight
    return 0


def index(request):
    '''The homepage'''
    term = request.POST.get('term')
    deltas = {}
    if term:
        times = []
        times.append(datetime.now())
        t = thingiverse.Thingiverse({'client_id': KEY, 'client_secret': SECRET, 'redirect_uri': ''})
        t.connect(TOKEN)
        results = t.keyword_search(term)
        times.append(datetime.now())

        total = {}
        normalized = {}
        weights = {}

        for feature in FEATURES:
            value = request.POST.get(feature)
            if value:
                total[feature] = 0
                weight = request.POST.get(feature + '_weight')
                if weight:
                    weights[feature] = int(weight)
                else:
                    weights[feature] = 1

        # When nothing is found a dictionary is returned
        # {'error': 'Not Found'}
        if type(results) != list:
            results = []
            # This is not very nice, I know
            now = datetime.now()
            times.append(now)
            times.append(now)

        for result in results:
            # Get more info
            times.append(datetime.now())
            result['detail'] = t.get_thing(int(result['id']))
            times.append(datetime.now())

            # Calculate age
            added = datetime.strptime(result['detail']['added'][:DATE_LENGTH], DATE_FORMAT)
            delta = datetime.now() - added
            result['detail']['age'] = delta.days

            result['absolute'] = {}
            result['relative'] = {}

            # Calculate numeric constrains
            for feature in total:
                # This should really use "in STRINGS", but creator name and thing name are differently saved in the dict
                if feature == 'creator':
                    result['absolute'][feature] = distance(result[feature]['name'], request.POST.get(feature))
                elif feature == 'name':
                    result['absolute'][feature] = distance(result[feature], request.POST.get(feature))
                else:
                    result['absolute'][feature] = abs(int(result['detail'][feature]) - int(request.POST.get(feature)))

                # Store total
                total[feature] += result['absolute'][feature]

        # Normalize calculated values
        for result in results:
            result['penalty'] = 0.0
            for feature in total:
                result['relative'][feature] = normalize(result['absolute'][feature], total[feature], weights[feature])
                result['penalty'] += result['relative'][feature]
        results = sorted(results, key=lambda k: k['penalty'])

        times.append(datetime.now())
        
        # Calculate times
        deltas['total'] = times[4] - times[0]
        deltas['api'] = (times[1] - times[0]) + (times[3] - times[2])
        deltas['noapi'] = deltas['total'] - deltas['api']
    else:
        term = ""
        results = []
    return render(request, 'index.html', {'term': term,
                                          'results': results,
                                          'post': request.POST,
                                          'deltas': deltas})
