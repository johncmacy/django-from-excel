from datetime import datetime
import os
import numpy as np
import pandas as pd
import json

from django.template.defaultfilters import slugify
from django.core import management
from django.core.management.base import BaseCommand
from django.conf import settings
from pandas.core.series import Series

class Field:
    def __init__(self, series:Series):
        self.field_name = series.name
        self.series = series
        self.series_without_nulls = Series([v for v in series.dropna()])
        self.dtype = self.series_without_nulls.dtype
        self.duplicates = self.series_without_nulls.drop_duplicates()

    def is_nullable(self):
        return self.series.hasnans

    def has_duplicate_values(self):
        return bool(self.duplicates)

    def kwargs(self):

        kw = {}

        if str(self.dtype) == 'object':
            kw = {'max_length': max([len(str(cell_value)) for cell_value in self.series_without_nulls] or [1])}

        if str(self.dtype) == 'float64':
            def num_digits_and_precision(value:str) -> tuple:
                total_digits = len(value.replace('.', ''))
                dot = value.find('.')
                decimals = value[dot+1:]
                decimal_places = len(decimals)

                return total_digits, decimal_places

            all_num_digits_and_precision = [num_digits_and_precision(str(cell_value)) for cell_value in self.series_without_nulls]
            max_digits = max([n for n, _ in all_num_digits_and_precision] or [2])
            decimal_places = max([n for _, n in all_num_digits_and_precision] or [1])

            kw = {'max_digits': max_digits, 'decimal_places': decimal_places}

        if self.is_nullable():
            kw['null'] = True
            kw['blank'] = True

        return kw

    def kwargs_string(self):
        return ', '.join(f'{k}={v}' for k,v in self.kwargs().items())

    def field_type_and_kwargs(self):
        
        dtype_field_mapping = {
            'object': 'models.CharField({})',
            'bool': 'models.BooleanField({})',
            'int64': 'models.IntegerField({})',
            'float64': 'models.DecimalField({})',
        }

        return dtype_field_mapping[str(self.dtype)]

    def __str__(self):
        return f'{self.field_name} = {self.field_type_and_kwargs().format(self.kwargs_string())}'

class Model:
    def __init__(self, class_name, dataframe):
        self.class_name = class_name
        self.columns = dataframe.columns
        self.fields = [Field(dataframe[column]) for column in dataframe.columns]

    def __str__(self):
        models_py = f'class {self.class_name}(models.Model):\r\t'
        models_py += '\r\t'.join([str(field) for field in self.fields])

        models_py += '\r\r\t'
        models_py += "__str__ = __repr__ = lambda self: f'{self.id}'"
        
        models_py += f"\r\r\t"
        models_py += "def __str__(self):"
        models_py += "\r\t\treturn f'{self.id}'"

        return models_py


def convert(filepath:str, app:str, overwrite=False, migrate=False, loaddata=False):

    df = pd.read_excel(filepath, dtype=object)

    df.rename(columns={
        column: slugify(column).replace('-', '_') 
        for column 
        in df.columns
    }, inplace=True)

    main_model = Model('ConvertedModel', df)

    models = [main_model]


    # models.py
    models_py = f'# Created by django-from-excel at {datetime.now()}\r\r'
    models_py += 'from django.db import models\r\r'
    models_py += '\r\r'.join(str(model) for model in models)


    # admin.py
    admin_py = f'# Created by django-from-excel at {datetime.now()}\r\r'
    admin_py += 'from django.contrib import admin\r'
    admin_py += 'from .models import *\r\r'
    admin_py += '\r'.join([f'admin.site.register({model.class_name})\r' for model in models])
    
    suffix ='' if overwrite else f'_{hex(abs(hash(datetime.now())))[2:10]}'
    models_py_filepath = os.path.join(app, f'models{suffix}.py')

    with open(models_py_filepath, 'w') as f:
        f.write(models_py)
    
    admin_py_filepath = os.path.join(app, f'admin{suffix}.py')

    with open(admin_py_filepath, 'w') as f:
        f.write(admin_py)

    print(f'Generated {admin_py_filepath} and {models_py_filepath}')

    if overwrite and migrate:
        management.call_command('makemigrations')
        management.call_command('migrate')

        if loaddata:
            df_dict = df.to_dict(orient='records')

            fixture = [
                {
                    'model': f'{app}.{model_name.lower()}',
                    'pk': i,
                    'fields': fields,
                }
                for i, fields
                in enumerate(df_dict, start=1)
            ]

            fixtures_directory = os.path.join(settings.BASE_DIR, app, 'fixtures')
            fixtures_filepath = os.path.join(fixtures_directory, f'{model_name.lower()}.json')
            if not os.path.exists(fixtures_directory):
                os.makedirs(fixtures_directory)
            with open(fixtures_filepath, 'w') as f:
                json.dump(fixture, f)

            management.call_command('loaddata', f'{model_name.lower()}.json', app=app)

    print(f'Complete. View the data at http://localhost:8000/admin/')



class Command(BaseCommand):
    help = 'Generates Django models from a spreadsheet file.'

    def add_arguments(self, parser):
        parser.add_argument('filepath', nargs='+', type=str)
        parser.add_argument('app', nargs='+', type=str)
        parser.add_argument('--overwrite', action='store_true', help='Overwrite existing models.py and admin.py files?')
        parser.add_argument('--migrate', action='store_true', help='Run makemigrations and migrate when done?')
        parser.add_argument('--loaddata', action='store_true', help='Load data after migrations are complete?')

    def handle(self, *args, **options):

        filepath = options['filepath'][0]
        app = options['app'][0]
        overwrite = options['overwrite']
        migrate = options['migrate']
        loaddata = options['loaddata']

        self.stdout.write(f'Converting {filepath} to models in {app}')

        convert(filepath, )



