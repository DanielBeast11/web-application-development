import uuid
from datetime import timedelta

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .calc import calc
from .permissions import IsModerator, IsAuthenticated, IsBuyer
from .redis import session_storage
from .serializers import *
from .utils import get_session, get_draft_depreciation, identity_user


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'car_name',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
def search_cars(request):
    car_name = request.GET.get("car_name", "")

    cars = Car.objects.filter(status=1)
    if car_name:
        cars = cars.filter(name__icontains=car_name)

    serializer = CarsSerializer(cars, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_car_by_id(request, car_id):
    if not Car.objects.filter(pk=car_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    car = Car.objects.get(pk=car_id)
    serializer = CarSerializer(car)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=CarSerializer)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_car(request, car_id):
    if not Car.objects.filter(pk=car_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    car = Car.objects.get(pk=car_id)

    serializer = CarSerializer(car, data=request.data, partial=True)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='POST', request_body=CarAddSerializer)
@api_view(["POST"])
@permission_classes([IsModerator])
def create_car(request):
    serializer = CarSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Car.objects.create(**serializer.validated_data)

    cars = Car.objects.filter(status=1)
    serializer = CarSerializer(cars, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
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
@permission_classes([IsBuyer])
def add_car_to_depreciation(request, car_id):
    if not Car.objects.filter(pk=car_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    car = Car.objects.get(pk=car_id)

    draft_depreciation = get_draft_depreciation(request)

    if draft_depreciation is None:
        draft_depreciation = Depreciation.objects.create()
        draft_depreciation.owner = identity_user(request)
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


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE),
    ]
)
@api_view(["POST"])
@permission_classes([IsModerator])
@parser_classes((MultiPartParser,))
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


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'status',
            openapi.IN_QUERY,
            type=openapi.TYPE_NUMBER
        ),
        openapi.Parameter(
            'date_formation_start',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'date_formation_end',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_depreciations(request):
    status = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    depreciations = Depreciation.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        depreciations = depreciations.filter(owner=user)

    if status > 0:
        depreciations = depreciations.filter(status=status)

    if date_formation_start and parse_datetime(date_formation_start):
        depreciations = depreciations.filter(date_formation__gt=parse_datetime(date_formation_start) - timedelta(days=1))

    if date_formation_end and parse_datetime(date_formation_end):
        depreciations = depreciations.filter(date_formation__lt=parse_datetime(date_formation_end) + timedelta(days=1))

    serializer = DepreciationsSerializer(depreciations, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsBuyer])
def get_cart_info(request):
    resp = {
        "cars_count": 0,
        "draft_depreciation": 0
    }

    draft_depreciation = get_draft_depreciation(request)
    if draft_depreciation:
        cars = CarDepreciation.objects.filter(depreciation=draft_depreciation)
        resp = {
            "cars_count": cars.count(),
            "draft_depreciation": draft_depreciation.pk
        }

    return Response(resp)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_depreciation_by_id(request, depreciation_id):
    if not Depreciation.objects.filter(pk=depreciation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    depreciation = Depreciation.objects.get(pk=depreciation_id)

    user = identity_user(request)
    if not user.is_superuser and depreciation.owner != user:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = DepreciationSerializer(depreciation, many=False)
    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=DepreciationSerializer)
@api_view(["PUT"])
@permission_classes([IsBuyer])
def update_depreciation(request, depreciation_id):
    user = identity_user(request)
    if not Depreciation.objects.filter(pk=depreciation_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    depreciation = Depreciation.objects.get(pk=depreciation_id)
    serializer = DepreciationSerializer(depreciation, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsBuyer])
def update_status_user(request, depreciation_id):
    user = identity_user(request)
    if not Depreciation.objects.filter(pk=depreciation_id, owner=user).exists():
        return Response({
            "error": "амортизация не найден"
        }, status=status.HTTP_404_NOT_FOUND)

    depreciation = Depreciation.objects.get(pk=depreciation_id)

    if depreciation.status != 1:
        return Response({
            "error": "амортизация не в том статусе"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if not depreciation.price:
        return Response({
            "error": "поле price не заполнено"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    depreciation.status = 2
    depreciation.date_formation = timezone.now()
    depreciation.save()

    serializer = DepreciationSerializer(depreciation)
    return Response(serializer.data)


@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_NUMBER),
        }
    )
)
@api_view(["PUT"])
@permission_classes([IsModerator])
def update_status_admin(request, depreciation_id):
    if not Depreciation.objects.filter(pk=depreciation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])
    if request_status not in [3, 4]:
        return Response({
            "error": "некорректный status"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    depreciation = Depreciation.objects.get(pk=depreciation_id)

    if depreciation.status != 2:
        return Response({
            "error": "амортизация не в том статусе"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        serializer = DepreciationSerializer(depreciation)
        depreciation.summ = calc(serializer.data)

    depreciation.date_complete = timezone.now()
    depreciation.status = request_status
    depreciation.moderator = identity_user(request)
    depreciation.save()

    serializer = DepreciationSerializer(depreciation)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsBuyer])
def delete_depreciation(request, depreciation_id):
    user = identity_user(request)
    if not Depreciation.objects.filter(pk=depreciation_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    depreciation = Depreciation.objects.get(pk=depreciation_id)

    if depreciation.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    depreciation.status = 5
    depreciation.save()

    serializer = DepreciationSerializer(depreciation, many=False)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsBuyer])
def delete_car_from_depreciation(request, depreciation_id, car_id):
    user = identity_user(request)
    if not Depreciation.objects.filter(pk=depreciation_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not CarDepreciation.objects.filter(depreciation_id=depreciation_id, car_id=car_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = CarDepreciation.objects.get(depreciation_id=depreciation_id, car_id=car_id)
    item.delete()

    items = CarDepreciation.objects.filter(depreciation_id=depreciation_id)
    data = [CarItemSerializer(item.car, context={"mileage": item.mileage}).data for item in items]

    return Response(data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='PUT', request_body=CarDepreciationSerializer)
@api_view(["PUT"])
@permission_classes([IsBuyer])
def update_car_in_depreciation(request, depreciation_id, car_id):
    user = identity_user(request)
    if not Depreciation.objects.filter(pk=depreciation_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not CarDepreciation.objects.filter(car_id=car_id, depreciation_id=depreciation_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    depreciation = Depreciation.objects.get(pk=depreciation_id)
    if depreciation.status != 1:
        return Response({
            "error": "Некорректный статус амортизации"
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    item = CarDepreciation.objects.get(car_id=car_id, depreciation_id=depreciation_id)

    serializer = CarDepreciationSerializer(item, data=request.data, partial=True)

    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_201_CREATED)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_200_OK)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    session = get_session(request)
    session_storage.delete(session)

    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('session_id')

    return response


@api_view(["GET"])
def user_info(request):
    user = identity_user(request)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='PUT', request_body=UserUpdateProfileSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = identity_user(request)

    serializer = UserUpdateProfileSerializer(user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data)
