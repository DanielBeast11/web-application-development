import random
from datetime import timedelta

from django.contrib.auth import authenticate
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import *


def get_draft_depreciation():
    return Depreciation.objects.filter(status=1).first()


def get_user():
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    return User.objects.filter(is_superuser=True).first()


@api_view(["GET"])
def search_cars(request):
    car_name = request.GET.get("car_name", "")

    cars = Car.objects.filter(status=1)

    if car_name:
        cars = cars.filter(name__icontains=car_name)

    serializer = CarsSerializer(cars, many=True)

    draft_depreciation = get_draft_depreciation()

    resp = {
        "cars": serializer.data,
        "cars_count": CarDepreciation.objects.filter(
            depreciation=draft_depreciation).count() if draft_depreciation else None,
        "draft_depreciation": draft_depreciation.pk if draft_depreciation else None
    }

    return Response(resp)


@api_view(["GET"])
def get_car_by_id(request, car_id):
    if not Car.objects.filter(pk=car_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    car = Car.objects.get(pk=car_id)
    serializer = CarSerializer(car)

    return Response(serializer.data)


@api_view(["PUT"])
def update_car(request, car_id):
    if not Car.objects.filter(pk=car_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    car = Car.objects.get(pk=car_id)

    serializer = CarSerializer(car, data=request.data, partial=True)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_car(request):
    serializer = CarSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Car.objects.create(**serializer.validated_data)

    cars = Car.objects.filter(status=1)
    serializer = CarSerializer(cars, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_car(request, car_id):
    if not Car.objects.filter(pk=car_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    car = Car.objects.get(pk=car_id)
    car.status = 2
    car.save()

    cars = Car.objects.filter(status=1)
    serializer = CarSerializer(cars, many=True)

    return Response(serializer.data)


@api_view(["POST"])
def add_car_to_depreciation(request, car_id):
    if not Car.objects.filter(pk=car_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    car = Car.objects.get(pk=car_id)

    draft_depreciation = get_draft_depreciation()

    if draft_depreciation is None:
        draft_depreciation = Depreciation.objects.create()
        draft_depreciation.owner = get_user()
        draft_depreciation.date_created = timezone.now()
        draft_depreciation.save()

    if CarDepreciation.objects.filter(depreciation=draft_depreciation, car=car).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    item = CarDepreciation.objects.create(
        depreciation=draft_depreciation,
        car=car
    )
    item.save()

    serializer = DepreciationSerializer(draft_depreciation)
    return Response(serializer.data["cars"])


@api_view(["POST"])
def update_car_image(request, car_id):
    if not Car.objects.filter(pk=car_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    car = Car.objects.get(pk=car_id)

    image = request.data.get("image")
    if image is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    car.image = image
    car.save()

    serializer = CarSerializer(car)
    return Response(serializer.data)


@api_view(["GET"])
def search_depreciations(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    depreciations = Depreciation.objects.exclude(status__in=[1, 5])

    if status > 0:
        depreciations = depreciations.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        depreciations = depreciations.filter(date_formation__gt=parse_datetime(date_formation_start) - timedelta(days=1))

    if date_formation_end and parse_datetime(date_formation_end):
        depreciations = depreciations.filter(date_formation__lt=parse_datetime(date_formation_end) + timedelta(days=1))

    serializer = DepreciationsSerializer(depreciations, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_depreciation_by_id(request, depreciation_id):
    if not Depreciation.objects.filter(pk=depreciation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    depreciation = Depreciation.objects.get(pk=depreciation_id)
    serializer = DepreciationSerializer(depreciation, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_depreciation(request, depreciation_id):
    if not Depreciation.objects.filter(pk=depreciation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    depreciation = Depreciation.objects.get(pk=depreciation_id)
    serializer = DepreciationSerializer(depreciation, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_user(request, depreciation_id):
    if not Depreciation.objects.filter(pk=depreciation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    depreciation = Depreciation.objects.get(pk=depreciation_id)

    if depreciation.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    depreciation.status = 2
    depreciation.date_formation = timezone.now()
    depreciation.save()

    serializer = DepreciationSerializer(depreciation, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, depreciation_id):
    if not Depreciation.objects.filter(pk=depreciation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    depreciation = Depreciation.objects.get(pk=depreciation_id)

    if depreciation.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        depreciation.summ = random.randint(1, 10)

    depreciation.date_complete = timezone.now()
    depreciation.status = request_status
    depreciation.moderator = get_moderator()
    depreciation.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
def delete_depreciation(request, depreciation_id):
    if not Depreciation.objects.filter(pk=depreciation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    depreciation = Depreciation.objects.get(pk=depreciation_id)

    if depreciation.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    depreciation.status = 5
    depreciation.save()

    serializer = DepreciationSerializer(depreciation, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
def delete_car_from_depreciation(request, depreciation_id, car_id):
    if not CarDepreciation.objects.filter(depreciation_id=depreciation_id, car_id=car_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = CarDepreciation.objects.get(depreciation_id=depreciation_id, car_id=car_id)
    item.delete()

    items = CarDepreciation.objects.filter(depreciation_id=depreciation_id)
    data = [CarItemSerializer(item.car, context={"mileage": item.mileage}).data for item in items]

    return Response(data, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_car_in_depreciation(request, depreciation_id, car_id):
    if not CarDepreciation.objects.filter(car_id=car_id, depreciation_id=depreciation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = CarDepreciation.objects.get(car_id=car_id, depreciation_id=depreciation_id)

    serializer = CarDepreciationSerializer(item, data=request.data, partial=True)

    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response(status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data)