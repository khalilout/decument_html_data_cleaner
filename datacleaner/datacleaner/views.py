from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import csv
import os
import json
from django.conf import settings

# URL du serveur Flask sur Render
FLASK_URL = "https://flask-data-cleaner-1.onrender.com/api/clean"

def index(request):
    return render(request, 'datacleaner/upload.html')

@csrf_exempt
def upload(request):
    if request.method == 'POST':

        if 'datafile' not in request.FILES:
            return JsonResponse({'error': 'Aucun fichier fourni'}, status=400)

        datafile = request.FILES['datafile']
        outlier_method = request.POST.get('outlier_method', 'iqr')

        allowed_extensions = ['csv', 'txt', 'xls', 'xlsx', 'json', 'xml']
        file_extension = datafile.name.split('.')[-1].lower()

        if file_extension not in allowed_extensions:
            return JsonResponse({'error': 'Format de fichier non autorise'}, status=400)

        files = {'file': (datafile.name, datafile.read(), datafile.content_type)}
        data  = {'outlier_method': outlier_method}

        try:
            response = requests.post(FLASK_URL, files=files, data=data, timeout=60)

            if response.status_code != 200:
                return JsonResponse({
                    'error': f'Erreur Flask (code {response.status_code}): {response.text}'
                }, status=500)

            cleaned_path = os.path.join(settings.MEDIA_ROOT, 'cleaned.csv')
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            with open(cleaned_path, 'wb') as f:
                f.write(response.content)

            with open(cleaned_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.DictReader(f)
                data_list = list(csv_reader)

            stats_header = response.headers.get('X-Data-Stats')
            stats = json.loads(stats_header) if stats_header else {}

            return JsonResponse({'data': data_list, 'stats': stats}, safe=False)

        except requests.exceptions.ConnectionError:
            return JsonResponse({'error': 'Impossible de se connecter au serveur Flask.'}, status=503)
        except requests.exceptions.Timeout:
            return JsonResponse({'error': 'Le serveur Flask a mis trop de temps a repondre.'}, status=504)
        except Exception as e:
            return JsonResponse({'error': f'Erreur: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Methode non autorisee'}, status=405)


def download(request):
    cleaned_path = os.path.join(settings.MEDIA_ROOT, 'cleaned.csv')
    if os.path.exists(cleaned_path):
        with open(cleaned_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="cleaned.csv"'
            return response
    return HttpResponse('Fichier non trouve', status=404)