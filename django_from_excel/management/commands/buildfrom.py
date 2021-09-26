from datetime import datetime
import os
import numpy as np
import pandas as pd
import json

from django.template.defaultfilters import slugify
from django.core import management
from django.core.management.base import BaseCommand
from django.conf import settings
from pandas.core.frame import DataFrame
from pandas.core.series import Series

class Field:
    def __init__(self, series:Series):
        self.field_name = series.name
        self.series = series
        self.is_nullable = self.series.hasnans
        self.series_without_nulls = Series([v for v in series.dropna()])
        self.dtype = str(self.series_without_nulls.dtype)
        self.duplicated = self.series_without_nulls.duplicated()
        self.has_duplicate_values = any(self.duplicated)
        self.duplicates = self.series_without_nulls.drop_duplicates()
        self.choices = None
        self.field_type_and_kwargs = self.get_field_type_and_kwargs()

    def get_field_type_and_kwargs(self):
        field_type = ''
        kwargs = {}

        if self.dtype == 'object':
            if self.has_duplicate_values:
                field_type = 'models.IntegerField({})'
                self.choices = {i: value for (i, value) in enumerate(self.duplicates.values, start=1)}
                self.choices_reverse = {v: k for k, v in self.choices.items()}
                kwargs['choices'] = [(k,v) for k,v in self.choices.items()]

                self.series = Series([self.choices_reverse.get(value) for value in self.series])

                # self.foreign_key_model = Model(self.field_name, DataFrame())

            else:
                field_type = 'models.CharField({})'
                kwargs['max_length'] = max([len(str(cell_value)) for cell_value in self.series_without_nulls] or [1])

        elif self.dtype == 'bool':
            field_type = 'models.BooleanField({})'

        elif self.dtype == 'int64':
            field_type = 'models.IntegerField({})'

        elif self.dtype == 'float64':
            field_type = 'models.DecimalField({})'
        
            def num_digits_and_precision(value:str) -> tuple:
                total_digits = len(value.replace('.', ''))
                dot = value.find('.')
                decimals = value[dot+1:]
                decimal_places = len(decimals)

                return total_digits, decimal_places

            all_num_digits_and_precision = [num_digits_and_precision(str(cell_value)) for cell_value in self.series_without_nulls]
            max_digits = max([n for n, _ in all_num_digits_and_precision] or [2])
            decimal_places = max([n for _, n in all_num_digits_and_precision] or [1])

            kwargs['max_digits'] = max_digits
            kwargs['decimal_places'] = decimal_places

        elif self.dtype == 'datetime64[ns]':
            field_type = 'models.DateTimeField({})'

        if self.is_nullable:
            kwargs['null'] = True
            kwargs['blank'] = True

        return field_type.format(', '.join(f'{k}={v}' for k,v in kwargs.items()))

    def __str__(self):
        return f'{self.field_name} = {self.field_type_and_kwargs}'

class Model:
    def __init__(self, app, class_name, dataframe:DataFrame):
        self.app = app
        self.class_name = class_name

        self.columns = dataframe.columns
        self.fields = [Field(dataframe[column]) for column in dataframe.columns]
        # self.related_models = [field.foreign_key_model for field in self.fields]

        # replace fields that have choices with the key instead of the value
        # self.dataframe = dataframe.replace(to_replace={field: field for field in self.fields}, value={})
        self.dataframe = dataframe
        for field in self.fields:
            if field.choices:
                self.dataframe[field.field_name] = field.series

    def __str__(self):
        s = f'class {self.class_name}(models.Model):\r\t'
        s += '\r\t'.join([str(field) for field in self.fields])

        s += '\r\r\t'
        s += "__str__ = __repr__ = lambda self: f'{self.id}'"
        
        s += f"\r\r\t"
        s += "def __str__(self):"
        s += "\r\t\treturn f'{self.id}'"

        return s

    def fixture(self):
        df_as_dict = self.dataframe.to_dict(orient='records')
        for record in df_as_dict:
            for key, value in record.items():
                if str(value).lower() == 'nan':
                    record[key] = None

        return [
            {
                'model': f'{self.app}.{self.class_name.lower()}',
                'pk': i,
                'fields': {k: None if str(v).lower() == 'nan' else v for k, v in fields.items()},
            }
            for i, fields
            in enumerate(df_as_dict, start=1)
        ]

class Converter:
    def __init__(self, filepath:str, app:str, overwrite=False, migrate=False, loaddata=False, dev_mode=False):
        self.filepath = filepath
        self.app = app
        self.overwrite = overwrite
        self.migrate = migrate
        self.loaddata = loaddata

        self.dev_mode = dev_mode

        self.files_suffix ='' if overwrite else f'_{hex(abs(hash(datetime.now())))[2:10]}'

    def convert(self):

        self.generate_models()
        self.create_models_dot_py()
        self.create_admin_dot_py()

        if self.overwrite and self.migrate:
            if not self.dev_mode:
                management.call_command('makemigrations')
                management.call_command('migrate')

            if self.loaddata:
                self.create_fixtures()

                if not self.dev_mode:
                    management.call_command('loaddata', *self.fixture_filenames(), app=self.app)

        print(f'Complete. Run server and view the data at http://localhost:8000/admin/')

    def generate_models(self):
        df = pd.read_excel(self.filepath, dtype=object)

        df.rename(columns={
            column: slugify(column).replace('-', '_') 
            for column 
            in df.columns
        }, inplace=True)

        self.main_model = Model(self.app, 'ConvertedModel', df)
        self.models = [self.main_model]

    def create_models_dot_py(self):
        file_contents = f'# Created by django-from-excel at {datetime.now()}\r\r'
        file_contents += 'from django.db import models\r\r'
        file_contents += '\r\r'.join(str(model) for model in self.models)

        filepath = os.path.join(self.app, f'models{self.files_suffix}.py')
        with open(filepath, 'w') as f:
            f.write(file_contents)
        
    def create_admin_dot_py(self):
        file_contents = f'# Created by django-from-excel at {datetime.now()}\r\r'
        file_contents += 'from django.contrib import admin\r'
        file_contents += 'from .models import *\r\r'
        file_contents += '\r'.join([f'admin.site.register({model.class_name})\r' for model in self.models])
        
        filepath = os.path.join(self.app, f'admin{self.files_suffix}.py')
        with open(filepath, 'w') as f:
            f.write(file_contents)

    def create_fixtures(self):
        for model in self.models:
            dir = os.path.join(self.app, 'fixtures')
            if not os.path.exists(dir):
                os.makedirs(dir)

            filepath = os.path.join(dir, f'{model.class_name.lower()}.json')
            with open(filepath, 'w') as f:
                json.dump(model.fixture(), f)

    def fixture_filenames(self):
        return [f'{model.class_name.lower()}.json' for model in self.models]



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

        Converter(filepath, app, overwrite, migrate, loaddata).convert()
