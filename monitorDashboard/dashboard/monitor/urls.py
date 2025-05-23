from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.water_data, name='water_data'),
    path('graph/', views.water_level_graph, name='water_level_graph'),
    path('home/', views.home, name='home'),  
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('alerts/', views.alerts_list, name='alerts'),
    path('export/', views.export_csv, name='export_csv'),
    path('alerts/export/', views.export_alerts_csv, name='export_alerts_csv'),
    path('graph/data/', views.get_graph_data, name='get_graph_data'),
    path('settings/', views.settings_view, name='settings'),
    path('api/thresholds/<str:username>/', views.arduino_thresholds, name='arduino_thresholds'),
]
