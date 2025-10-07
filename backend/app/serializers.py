from rest_framework import serializers

from .models import *


class CarsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ("id", "name", "status", "vin", "image", "price", "image")


class CarSerializer(CarsSerializer):
    class Meta(CarsSerializer.Meta):
        fields = "__all__"


class DepreciationsSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Depreciation
        fields = "__all__"


class DepreciationSerializer(DepreciationsSerializer):
    cars = serializers.SerializerMethodField()
            
    def get_cars(self, depreciation):
        items = depreciation.cardepreciation_set.all()
        return [CarItemSerializer(item.car, context={"mileage": item.mileage}).data for item in items]


class CarItemSerializer(CarSerializer):
    mileage = serializers.SerializerMethodField()

    def get_mileage(self, _):
        return self.context.get("mileage")

    class Meta:
        model = Car
        fields = ("id", "name", "status", "vin", "image", "price", "mileage")


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
