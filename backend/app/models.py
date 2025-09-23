from django.db import models
from django.forms import model_to_dict
from django.utils import timezone

from django.contrib.auth.models import User


class Car(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    license_plate = models.CharField(max_length=100, verbose_name="Госномер", default="Unknown")
    VIN = models.CharField(max_length=100, verbose_name="VIN")
    price = models.IntegerField(verbose_name="Стоимость")
    image = models.ImageField(blank=True)
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
        db_table = "cars"
        ordering = ("pk",)

class DepreciationCalculation(models.Model):
    STATUS = (
        (1, 'Черновик'),
        (2, 'Сформирован'),
        (3, 'Завершён'),
        (4, 'Отклонён'),
        (5, 'Удалён'),
    )

    status = models.IntegerField(choices=STATUS, default=1, verbose_name="Статус")
    creation_date = models.DateTimeField(verbose_name="Дата создания", default=timezone.now)
    formation_date = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    completion_date = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Пользователь", null=True, related_name='user')
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Модератор", null=True, related_name='moderator')
    sum = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "Расчет амортизации №" + str(self.pk)
    
    def get_cars(self):
        return [
            {
                **model_to_dict(item.car),
                'mileage': item.mileage,
            }
            for item in CarDepreciationCalculation.objects.filter(depreciation_calculation=self)
        ]

    class Meta:
        verbose_name = "Расчёт"
        verbose_name_plural = "Расчёты"
        db_table = "depreciation_calculations"
        ordering = ('-formation_date',)

class CarDepreciationCalculation(models.Model):
    car = models.ForeignKey(Car, on_delete=models.DO_NOTHING)
    depreciation_calculation = models.ForeignKey(DepreciationCalculation, on_delete=models.DO_NOTHING)
    mileage = models.IntegerField(default = 0, verbose_name="Пробег (км)")

    def __str__(self):
        return "М-М №" + str(self.pk)

    class Meta:
        verbose_name = "М-М"
        verbose_name_plural = "М-М"
        db_table = "car_depreciation_calculation"
        ordering = ('pk', )
