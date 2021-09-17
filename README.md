# excel-tracker-to-django
Utility to convert an Excel tracker-style file to a Django project

## Purpose

This utility will be able to:

* Create an app using `py manage.py startapp core`.
* Add `core.apps.CoreConfig` to `settings.INSTALLED_APPS`.

* Read an Excel file of the user's choosing.

* Create a Django model, with fields for each column.
* Detect the datatype of each column, and map to Django field types
* Detect columns that should be foreign keys:
  * Create a model for the foreign key to point to.

* Add all models to `core.admin`.
  
* Optionally, write the rows as new records in the Sqlite database.


## Problem

Excel is the go-to application that managers and analysts use to track the status of items within their scope of work. Excel chosen because it is freely available and widely understood. However, Excel is not ideal:

* Sharing creates multiple versions, each of which can easily get out-of-sync.
* Data is not normalized, which can lead to integrity errors.
* It is difficult (or impossible) to build pre-defined views of the same data, which leads to:
  * duplication of data into multiple views, or
  * poorly-designed views that make it difficult to make the right decisions with the data.

On the other hand, fully-customized web apps are expensive and time-consuming to develop.

## Solution

This utility aims to help solve the problem by quickly converting an Excel tracker into a basically functioning Django app that can be interacted with using the Django admin interface.

## TODO's

1. Columns with boolean data *and* blanks are given the float64 dtype
2. Design to be run after a Django project and app have been created
3. Extend manage.py with `convertexceltracker` command (https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/)[https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/]

