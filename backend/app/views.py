from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Car, DepreciationCalculation, CarDepreciationCalculation
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import connection
from .calc import depreciation_calculation
import random

home_icon_url = "http://localhost:9000/images/home-icon.svg"
cart_icon_url = "http://localhost:9000/images/cart-icon.png"
no_cars_cart_icon_url = "http://localhost:9000/images/no-cars-cart-icon.png"

def cars_list(request):
    query = request.GET.get("car_name", "").lower()
    cars = Car.objects.all()
    if query:
        cars = cars.filter(Q(name__icontains=query))
    
    filtered_cars = [
        {
            "id": car.pk,
            "name": car.name,
            "license_plate": car.license_plate,
            "VIN": car.VIN,
            "price": car.price,
            "image_url": car.image.url if car.image else None,
            "description": car.description,
        }
        for car in cars
    ]

    draft_depreciation = DepreciationCalculation.objects.filter(status=1).first()
    car_count = len(draft_depreciation.get_cars()) if draft_depreciation else 0
    depreciation_id = draft_depreciation.id if draft_depreciation else None

    return render(
        request,
        "cars_list.html",
        {
            "cars": filtered_cars,
            "car_name": query,
            "count": car_count,
            "home_icon_url": home_icon_url,
            "cart_icon_url": cart_icon_url,
            "no_cars_cart_icon_url": no_cars_cart_icon_url,
            "depreciation_id": depreciation_id,
        }
    )

def car_detail(request, car_id: int):
    car = Car.objects.get(pk=car_id)
    
    car_data = {
        "id": car.pk,
        "name": car.name,
        "licence_plate": car.license_plate,
        "VIN": car.VIN,
        "price": car.price,
        "image_url": car.image.url if car.image else None,
        "description": car.description,
    }

    return render(request,
        "car_detail.html",
            {"car": car_data,
             "home_icon_url": home_icon_url})


def depreciation_detail(request, depreciation_id):
    depreciation = get_object_or_404(DepreciationCalculation, pk=depreciation_id)
    if depreciation.status == 5:
        return render(request, "404.html", {"home_icon_url": home_icon_url})

    car_depreciation_relations = CarDepreciationCalculation.objects.filter(depreciation_calculation=depreciation)

    depreciation_cars = []
    
    for dep_car in car_depreciation_relations:
        car = dep_car.car
        car_data = {
            'id': car.id,
            'name': car.name,
            'license_plate': car.license_plate,
            'VIN': car.VIN,
            'price': car.price,
            'image_url': car.image.url if car.image else '/static/default.png',
            'request_mileage': dep_car.mileage
        }
        depreciation_cars.append(car_data)

    total_depreciation = depreciation.sum if depreciation.sum is not None else depreciation_calculation(depreciation.get_cars())

    context = {
        "depreciation": depreciation,
        "depreciation_cars": depreciation_cars,
        "total_depreciation": total_depreciation,
        "home_icon_url": home_icon_url
    }

    return render(request, "depreciation_detail.html", context)

def add_car_to_draft_depreciation(request, car_id):
    if request.method == 'POST':
        car = get_object_or_404(Car, pk=car_id)
        draft_depreciation = DepreciationCalculation.objects.filter(status=1).first()
        if draft_depreciation is None:
            draft_depreciation = DepreciationCalculation.objects.create(
                status=1,
                user=User.objects.filter(is_superuser=False).first(),
                creation_date=timezone.now()
            )

        if CarDepreciationCalculation.objects.filter(
            depreciation_calculation=draft_depreciation, 
            car=car
        ).exists():
            return redirect('cars_list')

        CarDepreciationCalculation.objects.create(
            car=car,
            depreciation_calculation=draft_depreciation,
            mileage=0
        )

    return redirect('cars_list')

def delete_depreciation(request, depreciation_id):
    if not DepreciationCalculation.objects.filter(pk=depreciation_id).exists():
        return redirect("/")

    with connection.cursor() as cursor:
        cursor.execute("UPDATE depreciation_calculations SET status=5 WHERE id = %s", [depreciation_id])

    return redirect("/")