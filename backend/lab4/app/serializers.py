from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from .models import *


class CarsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    image = serializers.ImageField(required=True)
    vin = serializers.CharField(required=True)

    class Meta:
        model = Car
        fields = ("id", "name", "status", "vin", "license_plate", "price", "image")


class CarSerializer(CarsSerializer):
    class Meta(CarsSerializer.Meta):
        fields = "__all__"


class CarAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ("name", "description", "vin", "image")


class DepreciationBaseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Depreciation
        fields = "__all__"


class DepreciationsSerializer(DepreciationBaseSerializer):
    cars_count = serializers.SerializerMethodField()

    def get_cars_count(self, depreciation):
        items = depreciation.cardepreciation_set.all()
        return items.count()


class CarItemSerializer(CarSerializer):
    mileage = serializers.SerializerMethodField()

    @swagger_serializer_method(serializer_or_field=serializers.IntegerField(required=True))
    def get_mileage(self, _):
        return self.context.get("mileage", 0)

    class Meta:
        model = Car
        fields = ("id", "name", "status", "vin", "license_plate", "price", "image", "mileage")


class DepreciationSerializer(DepreciationBaseSerializer):
    cars = serializers.SerializerMethodField()

    @swagger_serializer_method(serializer_or_field=CarItemSerializer(many=True))
    def get_cars(self, depreciation):
        items = depreciation.cardepreciation_set.all()
        return [CarItemSerializer(item.car, context={"mileage": item.mileage}).data for item in items]


class CarDepreciationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarDepreciation
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', "is_superuser")


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserUpdateProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    username = serializers.CharField(write_only=True, required=False, allow_blank=True)
    email = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        instance = super().update(instance, validated_data)

        if password and password.strip() and not self.instance.check_password(password):
            instance.set_password(password)
            instance.save()

        return instance
