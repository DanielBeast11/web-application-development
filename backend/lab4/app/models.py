from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, User
from django.db import models


class Car(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(max_length=500, verbose_name="Описание", )
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(verbose_name="Фото", default="default.png", blank=True, null=True)

    license_plate = models.CharField(max_length=100, verbose_name="Госномер")
    vin = models.CharField(max_length=100, verbose_name="VIN")
    price = models.IntegerField(verbose_name="Стоимость")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
        db_table = "cars"
        ordering = ("pk",)


class Depreciation(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Создатель", related_name='owner',
                              null=True)
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Модератор", related_name='moderator',
                                  blank=True, null=True)

    # Поле пользователя
    price = models.IntegerField(blank=True, null=True)

    # Вычисляемое поле
    summ = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "Амортизация №" + str(self.pk)

    class Meta:
        verbose_name = "Амортизация"
        verbose_name_plural = "Амортизации"
        db_table = "depreciations"
        ordering = ('-date_formation',)


class CarDepreciation(models.Model):
    pk = models.CompositePrimaryKey("car_id", "depreciation_id")
    car = models.ForeignKey(Car, on_delete=models.DO_NOTHING)
    depreciation = models.ForeignKey(Depreciation, on_delete=models.DO_NOTHING)

    # Поле м-м
    mileage = models.IntegerField(default=0)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "car_depreciation"
        ordering = ('pk',)
