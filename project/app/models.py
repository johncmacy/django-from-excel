
# Created by excel-tracker-to-django at 2021-09-17 18:12:03.420007

from django.db import models

class ConvertedModel(models.Model):
    vin = models.CharField(max_length=17)
    year = models.IntegerField()
    make = models.CharField(max_length=9)
    model = models.CharField(max_length=14)
    mileage = models.IntegerField()
    color = models.CharField(max_length=5)
    engine_size_liters = models.DecimalField(max_digits=2, decimal_places=1)
    fuel_type = models.CharField(max_length=8)
    avg_mpg = models.DecimalField(max_digits=15, decimal_places=13)
    is_leased = models.BooleanField()

    __str__ = __repr__ = lambda self: f'{self.id}'

    def __str__(self):
        return f'{self.id}'

        