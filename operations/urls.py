from django.urls import path
from . import views

app_name = 'operations'
urlpatterns = [
    path('reporting/', views.reports, name='reports'),
    path('<slug:slug>/', views.module_list, name='list'),
    path('<slug:slug>/create/', views.module_create, name='create'),
    path('<slug:slug>/<int:pk>/edit/', views.module_edit, name='edit'),
    path('<slug:slug>/<int:pk>/delete/', views.module_delete, name='delete'),
]
