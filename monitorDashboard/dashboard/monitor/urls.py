from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.water_data, name='water_data'),
    path('graph/', views.water_level_graph, name='water_level_graph'),
    path('home/', views.home, name='home'),  
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
