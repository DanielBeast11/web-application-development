from django.core.management.base import BaseCommand

from app.models import *
from app.calc import depreciation_calculation
from app.utils import *
from app.models import *

def add_users():
    User.objects.create_user("user", "user@user.com", "user", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "root", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")

def add_cars():
    Car.objects.create(
        name = 'GAZelle Business',
        license_plate = 'А911ВЕ77',
        VIN = 'XW8ZZZ61ZHG047860',
        price = 1200000,
        image = 'GAZelle1.jpeg',
        description = 'Легкий коммерческий грузовик GAZelle Business с дизельным двигателем Cummins ISF2.8'
    )
    Car.objects.create(
        name = 'Ford Transit',
        license_plate = 'А923ВЕ77',
        VIN = 'XW8ZZZ61ZHG457860',
        price = 2500000,
        image = 'FordTransit1.jpeg',
        description = 'Среднетоннажный фургон Ford Transit с дизельным двигателем 2.2 TDCi'
    )
    Car.objects.create(
        name = 'Iveco Daily 50C15',
        license_plate = 'C999XЕ77',
        VIN = 'XW8ZZZ61ZHG023860',
        price = 1300000,
        image = 'Iveco1.jpg',
        description = 'Легкий грузовик Iveco Daily 50C15 с дизельным двигателем F1A'
    )
    Car.objects.create(
        name = 'GAZelle Next',
        license_plate = 'А902ВЕ77',
        VIN = 'XW8ZZZ61ZHG047123',
        price = 1400000,
        image = 'GAZelle2.jpg',
        description = 'Модернизированная версия GAZelle Next с бензиновым двигателем EvoTech 2.7'
    )
    Car.objects.create(
        name = 'Ford Transit',
        license_plate = 'B123ВЕ77',
        VIN = 'XW8ZZZ61ZGD457860',
        price = 2100000,
        image = 'FordTransit2.jpg',
        description = 'Ford Transit с высокой крышей и дизельным двигателем 2.0 EcoBlue'
    )
    Car.objects.create(
        name = 'Iveco Daily 70C15',
        license_plate = 'C100XЕ77',
        VIN = 'XW8ZZZ61ZHG047341',
        price = 1700000,
        image = 'Iveco2.png',
        description = 'Тяжелый грузовик Iveco Daily 70C15 с дизельным двигателем F1C'
    )


def add_depreciation_calculations():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)
    cars = Car.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        user = random.choice(users)
        add_depreciation_calculation(status, cars, user, moderators)

    add_depreciation_calculation(1, cars, users[0], moderators)
    add_depreciation_calculation(2, cars, users[0], moderators)

def add_depreciation_calculation(status, cars, user, moderators):
    depreciation = DepreciationCalculation.objects.create()
    depreciation.status = status

    if status in [3, 4]:
        depreciation.moderator = random.choice(moderators)
        depreciation.completion_date = random_date()
        depreciation.formation_date = depreciation.completion_date - random_timedelta()
        depreciation.creation_date = depreciation.formation_date - random_timedelta()
    else:
        depreciation.formation_date = random_date()
        depreciation.creation_date = depreciation.formation_date - random_timedelta()

    depreciation.user = user

    for car in random.sample(list(cars), 3):
        item = CarDepreciationCalculation(
            depreciation_calculation=depreciation,
            car=car,
            mileage=random.randint(5000, 200000)
        )
        item.save()

    if status == 3:
        depreciation.sum = depreciation_calculation(depreciation.get_cars())
    
    depreciation.save()

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_cars()
        add_depreciation_calculations()
        print("База данных заполнена")