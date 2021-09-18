from django.test import TestCase
from django_from_excel import __version__

def test_version():
    assert __version__ == '0.1.0'
