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
        'license_plate': 'А911ВЕ77',
        'VIN': 'XW8ZZZ61ZHG047860',
        'price': 1200000,
        'img_key': 'GAZelle1.jpeg',
        'description': 'Легкий коммерческий грузовик GAZelle Business с дизельным двигателем Cummins ISF2.8'
    },
    {
        'id': 2,
        'name': 'Ford Transit',
        'license_plate': 'А923ВЕ77',
        'VIN': 'XW8ZZZ61ZHG457860',
        'price': 2500000,
        'img_key': 'FordTransit1.jpg',
        'description': 'Среднетоннажный фургон Ford Transit с дизельным двигателем 2.2 TDCi'
    },
    {
        'id': 3,
        'name': 'Iveco Daily 50C15',
        'license_plate': 'C999XЕ77',
        'VIN': 'XW8ZZZ61ZHG023860',
        'price': 1300000,
        'img_key': 'Iveco1.jpg',
        'description': 'Легкий грузовик Iveco Daily 50C15 с дизельным двигателем F1A'
    },
    {
        'id': 4,
        'name': 'GAZelle Next',
        'license_plate': 'А902ВЕ77',
        'VIN': 'XW8ZZZ61ZHG047123',
        'price': 1400000,
        'img_key': 'GAZelle2.jpg',
        'description': 'Модернизированная версия GAZelle Next с бензиновым двигателем EvoTech 2.7'
    },
    {
        'id': 5,
        'name': 'Ford Transit',
        'license_plate': 'B123ВЕ77',
        'VIN': 'XW8ZZZ61ZGD457860',
        'price': 2100000,
        'img_key': 'FordTransit2.jpg',
        'description': 'Ford Transit с высокой крышей и дизельным двигателем 2.0 EcoBlue'
    },
    {
        'id': 6,
        'name': 'Iveco Daily 70C15',
        'license_plate': 'C100XЕ77',
        'VIN': 'XW8ZZZ61ZHG047341',
        'price': 1700000,
        'img_key': 'Iveco2.png',
        'description': 'Тяжелый грузовик Iveco Daily 70C15 с дизельным двигателем F1C'
    }
]

depreciation_request = {
    "id": 1,
    "total_depreciation": 944200,
    "date": "07.09.2025",
    "status": "Черновик",
    "cars": [
        {
            "car_id": 2,
            "mileage": 100000,
        },
        {
            "car_id": 3,
            "mileage": 170000,
        }
    ],
}