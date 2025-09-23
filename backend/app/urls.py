from django.urls import path
from . import views

urlpatterns = [
    path('', views.cars_list, name='cars_list'),
    path('cars/<int:car_id>/', views.car_detail, name='car_detail'),
    path('cars/<int:car_id>/add_to_calculation/', views.add_car_to_draft_calculation, name='add_car_to_draft_calculation'),
    path('calculations/<int:calculation_id>/', views.calculation_detail, name='calculation_detail'),
    path('calculations/<int:calculation_id>/delete/', views.delete_calculation, name="delete_calculation")
]