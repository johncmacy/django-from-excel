from datetime import datetime
import numpy as np
import pandas as pd
from django.template.defaultfilters import random, slugify

def field_name(column_name):
    return slugify(column_name).replace('-', '_')

dtype_field_mapping = {
    'object': 'models.CharField({})',
    'bool': 'models.BooleanField({})',
    'int64': 'models.IntegerField({})',
    'float64': 'models.DecimalField({})',
}

def column_format_kwargs(series, dtype):

    print(series, dtype)

    kwargs = {}

    if str(dtype) == 'object':
        kwargs = {'max_length': max([len(str(cell_value)) for cell_value in series])}

    if str(dtype) == 'float64':
        def num_digits_and_precision(value:str) -> tuple:
            total_digits = len(value.replace('.', ''))
            dot = value.find('.')
            decimals = value[dot+1:]
            decimal_places = len(decimals)

            return total_digits, decimal_places

        all_num_digits_and_precision = [num_digits_and_precision(str(cell_value)) for cell_value in series]
        max_digits = max([n for n, _ in all_num_digits_and_precision])
        decimal_places = max([n for _, n in all_num_digits_and_precision])

        kwargs = {'max_digits': max_digits, 'decimal_places': decimal_places}

    # series_has_null_values = any([cell_value == '' for cell_value in series])
    series_has_null_values = random([True, False, False, False, False])
    if series_has_null_values:
        kwargs['null'] = True
        kwargs['blank'] = True

    return kwargs

def kwargs_string(kwargs):
    return ', '.join(f'{k}={v}' for k,v in kwargs.items())

def run():
    df = pd.read_excel('vehicle-fleet.xlsx')

    column_dtypes = [(column, df.dtypes[i]) for i, column in enumerate(df.columns)]

    fields = [
        (
            field_name(column),
            dtype_field_mapping[str(dtype)].format(kwargs_string(column_format_kwargs(df[column], dtype)))
        )
        for column, dtype
        in column_dtypes
    ]

    models_py = (f'''
# Created by excel-tracker-to-django at {datetime.now()}

from django.db import models

class ConvertedModel(models.Model):
    {"""
    """.join([" = ".join(field) for field in fields])}

    __str__ = __repr__ = lambda self: f\'{{self.id}}\'

    def __str__(self):
        return f\'{{self.id}}\'

''')

    print('saving to models.py')

    with open('models.py', 'w') as f:
        f.write(models_py)



if __name__ == '__main__':
    print('Converting...')
    run()
    print('Conversion complete')
    print('Ctrl+click to view models: ./models.py')
