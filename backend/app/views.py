from django.shortcuts import render
from django.http import Http404
from minio import Minio

client = Minio(
    "localhost:9000",
    access_key="minio",
    secret_key="minio124",
    secure=False
)

def get_image_url(key: str) -> str:
    return client.presigned_get_object("images", key)

cars = [
    {
        'id': 1,
        'name': 'GAZelle Business',
        'license_plate': 'А902ВЕ77',
        'VIN': 'XW8ZZZ61ZHG047860',
        'mileage': 120000,
        'price': 1200000,
        'img_key': 'GAZelle1.jpeg',
        'description': 'Легкий коммерческий грузовик GAZelle Business с дизельным двигателем Cummins ISF2.8'
    },
    {
        'id': 2,
        'name': 'Ford Transit',
        'license_plate': 'А923ВЕ77',
        'VIN': 'XW8ZZZ61ZHG457860',
        'mileage': 100000,
        'price': 2500000,
        'img_key': 'FordTransit1.jpeg',
        'description': 'Среднетоннажный фургон Ford Transit с дизельным двигателем 2.2 TDCi'
    },
    {
        'id': 3,
        'name': 'Iveco Daily 50C15',
        'license_plate': 'C999XЕ77',
        'VIN': 'XW8ZZZ61ZHG023860',
        'mileage': 170000,
        'price': 1300000,
        'img_key': 'Iveco1.jpg',
        'description': 'Легкий грузовик Iveco Daily 50C15 с дизельным двигателем F1A'
    },
    {
        'id': 4,
        'name': 'GAZelle Next',
        'license_plate': 'А902ВЕ77',
        'VIN': 'XW8ZZZ61ZHG047123',
        'mileage': 110000,
        'price': 1400000,
        'img_key': 'GAZelle2.jpg',
        'description': 'Модернизированная версия GAZelle Next с бензиновым двигателем EvoTech 2.7'
    },
    {
        'id': 5,
        'name': 'Ford Transit',
        'license_plate': 'B123ВЕ77',
        'VIN': 'XW8ZZZ61ZGD457860',
        'mileage': 150000,
        'price': 2100000,
        'img_key': 'FordTransit2.jpg',
        'description': 'Ford Transit с высокой крышей и дизельным двигателем 2.0 EcoBlue'
    },
    {
        'id': 6,
        'name': 'Iveco Daily 70C15',
        'license_plate': 'C999XЕ77',
        'VIN': 'XW8ZZZ61ZHG047341',
        'mileage': 165000,
        'price': 1400000,
        'img_key': 'Iveco2.png',
        'description': 'Тяжелый грузовик Iveco Daily 70C15 с дизельным двигателем F1C'
    }
]

order = {
    "id": 1,
    "date": "07.09.2025",
    "cars": [
        {
            "id": 1,
            "name": "Ford Transit",
            "license_plate": "А923ВЕ77",
            "VIN": "XW8ZZZ61ZHG457860",
            "mileage": 100000,
            "price": 2500000,
            "img_key": "FordTransit1.jpeg",
            "comment": "Основной грузовик",
            "depreciation": 500000
        },
        {
            "id": 2,
            "name": "Iveco Daily 50C15",
            "license_plate": "C999XЕ77",
            "VIN": "XW8ZZZ61ZHG023860",
            "mileage": 170000,
            "price": 1300000,
            "img_key": "Iveco1.jpg",
            "comment": "Резервный грузовик",
            "depreciation": 561000
        }
    ],
    "total_depreciation": 1061000
}

home_icon_url = get_image_url("home-icon.svg")
cart_icon_url = get_image_url("cart-icon.png")

def cars_list(request):
    query = request.GET.get("search", "").lower()
    filtered_cars = [c.copy() for c in cars if query in c['name'].lower()]

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
