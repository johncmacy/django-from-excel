
Have an Excel tool that you'd like to quickly convert to a Django project? `django-from-excel` is the answer.

## Features

1. Generates models.py file:
   1. Generate a Django model for each table/sheet in your Excel file
   2. Create appropriate field types for each of your table columns, with Pythonic naming
   3. TODO: Detect nullable columns
   4. TODO: Identify columns that should be foreign keys, and create corresponding models with choice fields
2. Generates admin.py file:
   1. Registers all models created in Step 1
3. Optionally creates migration files and migrates the schema
4. Optionally generates fixtures and loads data into your database

With a single command, you will be able to explore your data in the Django admin.

---

# Usage

The following instructions assume you already have a Django project and at least one app set up.

## Installation

``` sh
pip install django-from-excel
```

## Setup

Locate the Excel file that has the data you want to build models from. It should have a table of data, like this:

![Example Excel file](static/img/fleet.xlsx.png)

Copy this file to a location in the project that is easy to reference. The simplest approach is to place it in the same directory as `manage.py`, as that is where you'll need to run the command from.

Before continuing, make sure you have created an app, and that it is registered in `settings.INSTALLED_APPS`.

Add `django_from_excel` to `settings.INSTALLED_APPS`.

At this point, also confirm your database settings.

## Run

Example:

``` sh
manage.py buildfrom fleet.xlsx app --overwrite --migrate --loaddata
  ```

The following options are available for the `buildfrom` command:

**filepath:**

Required. The filepath or path/to/filepath for the Excel file to generate models from.

**app:**

Required. The app to generate `models.py` and `admin.py` files in. Must already exist, and must be listed in `settings.INSTALLED_APPS`.

**--overwrite:**

Will overwrite existing `admin.py` and `models.py` files in the target app; otherwise, a unique hex string will be appended to the file names, such as `models_120f77f8.py`.

WARNING: If you have existing models and specify `--overwrite`, they will be lost forever!

**--migrate:**

After generating the models, this will automatically run `manage.py makemigrations` and `manage.py migrate`.

**--loaddata:**

Once migrations are complete, this will generate a `convertedmodel.json` file in `<app>/fixtures`, and will then call the `manage.py loaddata convertedmodel.json <app>` command.
Must be used in conjunction with `--migrate`.

``` json
[
    {
        "model": "app.convertedmodel",
        "pk": 1,
        "fields": {
            "vin": "JN8AF5MV9BT005581",
            "year": 2021,
            "make": "Chevrolet",
            "model": "Silverado 1500",
            "mileage": 25000,
            "color": "White",
            "engine_size_liters": 6.2,
            "fuel_type": "gasoline",
            "avg_mpg": 24.5394832,
            "is_leased": true
        }
    }
]
```

## Inspect

View the `models.py` and `admin.py` files that were generated.

If you chose the `--migrate` option:

Log in to the [Django admin](http://localhost:8000/admin/). Your converted model(s) should be listed there.

![Converted models in Django admin](static/img/django-admin.png)

If you specified `--loaddata`:

Open the model, and you should have a record for each row in the original Excel file.

![Example record in converted model](static/img/converted-model.png)

## Eject

Once you are satisfied with the results, you can remove `django_from_excel` from `settings.INSTALLED_APPS` and uninstall `django-from-excel` and any other dependencies you don't need for your project.

TODO: Create an eject command to handle this automatically.

## Build Your Dream App

This is only intended to create a starting point. You'll want to inspect the models to make sure the field types are correct, you'll likely need to add some nullable fields or unique constraints, and you may need to spin some fields off into their own tables, with foreign keys linking back.

---

# Common Errors

## Unknown command: 'buildfrom'

Solution: Add `django_from_excel` to `settings.INSTALLED_APPS`.