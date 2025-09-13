from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'Django API is running',
        'mongodb': 'ready to connect'
    })
