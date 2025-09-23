from django.contrib import admin
from app.models import *

# Register your models here.
admin.site.register(Car)
admin.site.register(DepreciationCalculation)
admin.site.register(CarDepreciationCalculation)