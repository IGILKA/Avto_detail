from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('zakupki/', views.zakupka_list, name='zakupka_list'),
    path('zakupki/new/', views.zakupka_create, name='zakupka_create'),
    
    path('proizvodstvo/', views.proizvodstvo_list, name='proizvodstvo_list'),
    path('proizvodstvo/new/', views.proizvodstvo_create, name='proizvodstvo_create'),
    
    path('prodazhi/', views.prodazha_list, name='prodazha_list'),
    path('prodazhi/new/', views.prodazha_create, name='prodazha_create'),
    
    path('zarplata/', views.zarplata_list, name='zarplata_list'),
    path('zarplata/pay/<int:emp_id>/', views.zarplata_pay, name='zarplata_pay'),
    
    path('kredity/', views.kredity_form, name='kredity_form'),
    path('reports/', views.reports_dashboard, name='reports'),
    
    path('requests/', views.zayavki_list, name='zayavki_list'),
    path('requests/new/', views.zayavki_create, name='zayavki_create'),
    path('requests/<int:zayavka_id>/process/', views.zayavka_process, name='zayavka_process'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register_view, name='register'),
]
