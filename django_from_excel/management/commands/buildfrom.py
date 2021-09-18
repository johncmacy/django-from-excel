from datetime import datetime
import os
import numpy as np
import pandas as pd
import json

from django.template.defaultfilters import slugify
from django.core import management
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Generates Django models from a spreadsheet file.'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)
        parser.add_argument('app', nargs='+', type=str)
        parser.add_argument('--overwrite', action='store_true', help='Overwrite existing models.py and admin.py files?')
        parser.add_argument('--migrate', action='store_true', help='Run makemigrations and migrate when done?')
        parser.add_argument('--loaddata', action='store_true', help='Load data after migrations are complete?')

    def handle(self, *args, **options):

        filename = options['filename'][0]
        app = options['app'][0]
        overwrite = options['overwrite']
        migrate = options['migrate']
        loaddata = options['loaddata']

        self.stdout.write(f'Converting {filename} to models in {app}')

        def field_name(column_name):
            return slugify(column_name).replace('-', '_')

        dtype_field_mapping = {
            'object': 'models.CharField({})',
            'bool': 'models.BooleanField({})',
            'int64': 'models.IntegerField({})',
            'float64': 'models.DecimalField({})',
        }

        def column_format_kwargs(series, dtype):

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
            # series_has_null_values = random([True, False, False, False, False])
            series_has_null_values = False
            if series_has_null_values:
                kwargs['null'] = True
                kwargs['blank'] = True

            return kwargs

        def kwargs_string(kwargs):
            return ', '.join(f'{k}={v}' for k,v in kwargs.items())

        df = pd.read_excel(filename)

        # first rename the dataframe columns to their slugified equivalents
        for column in df.columns:
            df.rename(columns={column: field_name(column)}, inplace=True)

        df_dict = df.to_dict(orient='records')

        model_name = 'ConvertedModel'





        column_dtypes = [(column, df.dtypes[i]) for i, column in enumerate(df.columns)]

        fields = [
            (
                column,
                dtype_field_mapping[str(dtype)].format(kwargs_string(column_format_kwargs(df[column], dtype)))
            )
            for column, dtype
            in column_dtypes
        ]

        models_py = (f'''
# Created by django-from-excel at {datetime.now()}

from django.db import models

class {model_name}(models.Model):
    {"""
    """.join([" = ".join(field) for field in fields])}

    __str__ = __repr__ = lambda self: f\'{{self.id}}\'

    def __str__(self):
        return f\'{{self.id}}\'

        ''')

        admin_py = f'''
# Created by django-from-excel at {datetime.now()}

from django.contrib import admin
from .models import *

admin.site.register({model_name})

'''




        suffix ='' if overwrite else f'_{hex(abs(hash(datetime.now())))[2:10]}'
        models_py_filepath = os.path.join(app, f'models{suffix}.py')

        with open(models_py_filepath, 'w') as f:
            f.write(models_py)
        
        admin_py_filepath = os.path.join(app, f'admin{suffix}.py')

        with open(admin_py_filepath, 'w') as f:
            f.write(admin_py)

        self.stdout.write(self.style.SUCCESS(f'Generated {admin_py_filepath} and {models_py_filepath}'))

        if overwrite and migrate:
            management.call_command('makemigrations')
            management.call_command('migrate')

            if loaddata:
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
                fixtures_filename = os.path.join(fixtures_directory, f'{model_name.lower()}.json')
                if not os.path.exists(fixtures_directory):
                    os.makedirs(fixtures_directory)
                with open(fixtures_filename, 'w') as f:
                    json.dump(fixture, f)

                management.call_command('loaddata', f'{model_name.lower()}.json', app=app)

        self.stdout.write(self.style.SUCCESS(f'Complete. View the data at http://localhost:8000/admin/'))









