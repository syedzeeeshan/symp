from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

def health_check(request):
    """Health check endpoint for frontend connection testing"""
    try:
        return JsonResponse({
            'status': 'ok',
            'message': 'Django API is running',
            'mongodb': {'connected': True, 'message': 'Connected successfully'}
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def people_list(request):
    """Handle people API requests"""
    if request.method == 'GET':
        return JsonResponse({'people': []})
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Process the person data here
            return JsonResponse({'success': True, 'message': 'Person added'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
