from django.shortcuts import render
from django.http import Http404
from .models import cars, depreciation_request, get_image_url

home_icon_url = get_image_url("home-icon.svg")
cart_icon_url = get_image_url("cart-icon.png")

def cars_list(request):
    query = request.GET.get("search", "")
    lower_case_query = query.lower()
    filtered_cars = [c.copy() for c in cars if lower_case_query in c['name'].lower()]

    for car in filtered_cars:
        car['image_url'] = get_image_url(car['img_key'])

    count = len(depreciation_request['cars'])
    return render(
        request,
        "cars_list.html",
        {"cars": filtered_cars, "count": count, "search": query, "request": depreciation_request, "home_icon_url": home_icon_url, "cart_icon_url": cart_icon_url}
    )

def car_detail(request, car_id: int):
    car = next((c.copy() for c in cars if c['id'] == car_id), None)
    if not car:
        raise Http404("Автомобиль не найден")

    car['image_url'] = get_image_url(car['img_key'])
    return render(request, "car_detail.html", {"car": car, "request": depreciation_request, "home_icon_url": home_icon_url})

def request_detail(request, request_id: int):
    if depreciation_request['id'] != request_id:
        raise Http404("Заявка не найдена")

    depreciation_request_cars = []
    for car_data in depreciation_request['cars']:
        car = next((c.copy() for c in cars if c['id'] == car_data['car_id']), None)        
        if car:
            car['image_url'] = get_image_url(car['img_key'])
            car['request_mileage'] = car_data['mileage']
            depreciation_request_cars.append(car)
    
    return render(
        request,
        "request_detail.html",
        {"request": depreciation_request, "depreciation_request_cars": depreciation_request_cars, "home_icon_url": home_icon_url}
    )
