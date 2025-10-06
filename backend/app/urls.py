from django.urls import path
from . import views

urlpatterns = [
    path('', views.cars_list, name='cars_list'),
    path('cars/<int:car_id>/', views.car_detail, name='car_detail'),
    path('cars/<int:car_id>/add_to_depreciation/', views.add_car_to_draft_depreciation, name='add_car_to_draft_depreciation'),
    path('depreciations/<int:depreciation_id>/', views.depreciation_detail, name='depreciation_detail'),
    path('<int:depreciation_id>/delete/', views.delete_depreciation, name="delete_depreciation")
]