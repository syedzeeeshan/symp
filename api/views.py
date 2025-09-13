from django.http import JsonResponse

def health_check(request):
    try:
        return JsonResponse({
            'status': 'ok',
            'message': 'Django API is running',
            'mongodb': 'ready to connect'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })
