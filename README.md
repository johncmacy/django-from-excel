# django-from-excel
Automatically builds Django models from an Excel file

## Getting Started

The following instructions assume you already have a Django project and at least one app set up.

### Installation

``` sh
pip install django-from-excel
```

### Setup

Copy the Excel file you want to convert to a location in the project that is easy to reference. The simplest approach is to place it in the same directory as `manage.py`, as that is where you'll need to run the command from.

Before continuing, make sure you have created an app, and that it is registered in `settings.INSTALLED_APPS`.

Add `django_from_excel` to `settings.INSTALLED_APPS`.

At this point, also confirm your database settings.

### Run

``` sh
manage.py buildfrom <filename> <app>
```

!!! example
  If you placed a file called "tracker.xlsx" in the same directory as your manage.py file, and you have an app named "app", run:

  ``` sh
  manage.py buildfrom tracker.xlsx app
  ```

The following options are available for the `buildfrom` command:

**filename:**

Required. The filename or path/to/filename for the Excel file to generate models from.

**app:**

Required. The app to generate `models.py` and `admin.py` files in. Must already exist, and must be listed in `settings.INSTALLED_APPS`.

**--overwrite:**

Will overwrite existing `admin.py` and `models.py` files in the target app; otherwise, a unique hex string will be appended to the filenames, such as `models_120f77f8.py`.

!!! warning
  If you have existing models and specify `--overwrite`, they will be lost forever!

**--migrate:**

After generating the models, this will automatically run `manage.py makemigrations` and `manage.py migrate`.

**--loaddata:**

Once migrations are complete, this will generate a `convertedmodel.json` file in `<app>/fixtures`, and will then call the `manage.py loaddata convertedmodel.json <app>` command.
Must be used in conjunction with `--migrate`.

### Inspect

View the `models.py` and `admin.py` files that were generated.

If you chose the `--migrate` option:

Log in to the [Django admin](http://localhost:8000/admin/). Your converted model(s) should be listed there.

If you specified `--loaddata`:

Open the model, and you should have a record for each row in the original Excel file.

### Build Your Dream App

This is only intended to create a starting point. You'll want to inspect the models to make sure the field types are correct, and you'll likely need to add some nullable fields or unique constraints, and you may need to spin some fields off into their own tables, with foreign keys linking back. But, hopefully `django-from-excel` saved you time by quickly creating some Django models for you.

### Eject

Once you are satisfied with the results, you can remove `django_from_excel` from `settings.INSTALLED_APPS` and uninstall `django-from-excel` and any other dependencies you don't need for your project.

---

## TODO's

1. Columns with boolean data *and* blanks are given the float64 dtype
2. Detect duplicate data that should be in a foreign table, create ForeignKey field
3. Create an eject command





