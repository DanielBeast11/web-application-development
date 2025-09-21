from django.urls import path
from . import views

urlpatterns = [
    path("", views.cars_list, name="cars_list"),
    path("cars/<int:car_id>/", views.car_detail, name="car_detail"),
    path("depreciation_request/<int:request_id>/", views.request_detail, name="request_detail")
]