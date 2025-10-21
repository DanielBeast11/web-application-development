from django.core.management.base import BaseCommand

from app.calc import calc
from app.models import *
from app.serializers import DepreciationSerializer
from app.utils import *


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(2, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")


def add_cars():
    Car.objects.create(
        name = 'GAZelle Business',
        license_plate = 'А911ВЕ77',
        vin = 'XW8ZZZ61ZHG047860',
        price = 1200000,
        image = '1.png',
        description = 'Легкий коммерческий грузовик GAZelle Business с дизельным двигателем Cummins ISF2.8'
    )
    Car.objects.create(
        name = 'Ford Transit',
        license_plate = 'А923ВЕ77',
        vin = 'XW8ZZZ61ZHG457860',
        price = 2500000,
        image = '2.png',
        description = 'Среднетоннажный фургон Ford Transit с дизельным двигателем 2.2 TDCi'
    )
    Car.objects.create(
        name = 'Iveco Daily 50C15',
        license_plate = 'C999XЕ77',
        vin = 'XW8ZZZ61ZHG023860',
        price = 1300000,
        image = '3.png',
        description = 'Легкий грузовик Iveco Daily 50C15 с дизельным двигателем F1A'
    )
    Car.objects.create(
        name = 'GAZelle Next',
        license_plate = 'А902ВЕ77',
        vin = 'XW8ZZZ61ZHG047123',
        price = 1400000,
        image = '4.png',
        description = 'Модернизированная версия GAZelle Next с бензиновым двигателем EvoTech 2.7'
    )
    Car.objects.create(
        name = 'Ford Transit',
        license_plate = 'B123ВЕ77',
        vin = 'XW8ZZZ61ZGD457860',
        price = 2100000,
        image = '5.png',
        description = 'Ford Transit с высокой крышей и дизельным двигателем 2.0 EcoBlue'
    )
    Car.objects.create(
        name = 'Iveco Daily 70C15',
        license_plate = 'C100XЕ77',
        vin = 'XW8ZZZ61ZHG047341',
        price = 1700000,
        image = '6.png',
        description = 'Тяжелый грузовик Iveco Daily 70C15 с дизельным двигателем F1C'
    )


def add_depreciations():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)
    cars = Car.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_depreciation(status, cars, owner, moderators)

    # add_depreciation(1, cars, users[0], moderators)
    add_depreciation(2, cars, users[0], moderators)
    add_depreciation(3, cars, users[0], moderators)
    add_depreciation(4, cars, users[0], moderators)
    add_depreciation(5, cars, users[0], moderators)

    for _ in range(10):
        status = random.randint(2, 5)
        add_depreciation(status, cars, users[0], moderators)


def add_depreciation(status, cars, owner, moderators):
    depreciation = Depreciation.objects.create()
    depreciation.status = status

    if status in [3, 4]:
        depreciation.moderator = random.choice(moderators)
        depreciation.date_complete = random_date()
        depreciation.date_formation = depreciation.date_complete - random_timedelta()
        depreciation.date_created = depreciation.date_formation - random_timedelta()
    else:
        depreciation.date_formation = random_date()
        depreciation.date_created = depreciation.date_formation - random_timedelta()

    depreciation.price = random.randint(1, 10)

    depreciation.owner = owner

    for car in random.sample(list(cars), 3):
        item = CarDepreciation(
            depreciation=depreciation,
            car=car,
            mileage=random.randint(1, 10)
        )
        item.save()

    if status == 3:
        serializer = DepreciationSerializer(depreciation)
        depreciation.summ = calc(serializer.data)

    depreciation.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_cars()
        add_depreciations()
