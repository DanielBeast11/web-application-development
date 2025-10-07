from django.urls import path
from .views import *

urlpatterns = [
    path('api/cars/', search_cars),  # GET
    path('api/cars/<int:car_id>/', get_car_by_id),  # GET
    path('api/cars/<int:car_id>/update/', update_car),  # PUT
    path('api/cars/<int:car_id>/update_image/', update_car_image),  # POST
    path('api/cars/<int:car_id>/delete/', delete_car),  # DELETE
    path('api/cars/create/', create_car),  # POST
    path('api/cars/<int:car_id>/add_to_depreciation/', add_car_to_depreciation),  # POST

    path('api/depreciations/', search_depreciations),  # GET
    path('api/depreciations/<int:depreciation_id>/', get_depreciation_by_id),  # GET
    path('api/depreciations/<int:depreciation_id>/update/', update_depreciation),  # PUT
    path('api/depreciations/<int:depreciation_id>/update_status_user/', update_status_user),  # PUT
    path('api/depreciations/<int:depreciation_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/depreciations/<int:depreciation_id>/delete/', delete_depreciation),  # DELETE

    path('api/depreciations/<int:depreciation_id>/update_car/<int:car_id>/', update_car_in_depreciation),  # PUT
    path('api/depreciations/<int:depreciation_id>/delete_car/<int:car_id>/', delete_car_from_depreciation),  # DELETE

    path('api/users/register/', register), # POST
    path('api/users/login/', login), # POST
    path('api/users/logout/', logout), # POST
    path('api/users/<int:user_id>/update/', update_user) # PUT
]
