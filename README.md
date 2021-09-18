# django-from-excel
Utility to convert an Excel tracker-style file to a Django project

## Purpose

This utility will be able to:

* Read an Excel file of the user's choosing.

* Create a Django model from the table, with fields for each column.
* Detect the datatype of each column, and map to Django field types.
* Detect columns that should be foreign keys.
* Create corresponding models for the foreign keys to point to.
* Add models to `core.admin`.
* Run `manage.py makemigrations` and `manage.py migrate`.
* Optionally, write the rows as new records in the database.


## Problem

Excel is often used as a status tracker. It is chosen because it is readily available and widely understood. However, Excel is not ideal:

* Sharing creates multiple versions, each of which can easily get out-of-sync.
* Data is not normalized, which can lead to integrity errors.
* It is difficult (or impossible) to build pre-defined views of the same data, which leads to:
  * duplication of data into multiple views, or
  * poorly-designed views that make it difficult to make the right decisions with the data.

On the other hand, fully-customized web apps are expensive and time-consuming to develop.

## Solution

This utility aims to help solve the problem by quickly converting an Excel tracker into a basically functioning Django app that can be interacted with using the Django admin interface.

## Getting Started

Assumes you already have a Django project ("project") and app ("app") created, and can use the `manage.py` command.

1. TODO: installation instructions
2. Place tracker file to convert *from* in the same directory as `manage.py`
3. Run `py manage.py convertfrom tracker.xlsx app --overwrite`
4. Inspect `models.py` and `admin.py` in the `app` directory



---

## TODO's

1. Columns with boolean data *and* blanks are given the float64 dtype
2. Package for pypi.org
3. Create documentation branch in Github, publish using Github Pages and Material for MkDocs



