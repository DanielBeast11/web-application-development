from django.shortcuts import render
from django.http import Http404
from .models import cars, order, get_image_url

home_icon_url = get_image_url("home-icon.svg")
cart_icon_url = get_image_url("cart-icon.png")

def cars_list(request):
    query = request.GET.get("search", "")
    lower_case_query = query.lower()
    filtered_cars = [c.copy() for c in cars if lower_case_query in c['name'].lower()]

    for car in filtered_cars:
        car['image_url'] = get_image_url(car['img_key'])

    order_count = len(order['cars'])
    return render(
        request,
        "cars_list.html",
        {"cars": filtered_cars, "order_count": order_count, "search": query, "order": order, "home_icon_url": home_icon_url, "cart_icon_url": cart_icon_url}
    )

def car_detail(request, car_id: int):
    car = next((c.copy() for c in cars if c['id'] == car_id), None)
    if not car:
        raise Http404("Автомобиль не найден")

    car['image_url'] = get_image_url(car['img_key'])
    return render(request, "car_detail.html", {"car": car, "order": order, "home_icon_url": home_icon_url})

def order_detail(request, order_id: int):
    if order['id'] != order_id:
        raise Http404("Заявка не найдена")

    order_cars = []
    for c in order['cars']:
        c_copy = c.copy()
        c_copy['image_url'] = get_image_url(c['img_key'])
        order_cars.append(c_copy)

    return render(
        request,
        "order_detail.html",
        {"order": order, "order_cars": order_cars, "home_icon_url": home_icon_url}
    )
