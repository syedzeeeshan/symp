from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('people/', views.people_list, name='people_list'),  
]
