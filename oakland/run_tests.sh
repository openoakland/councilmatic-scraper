#!/bin/sh

export PYTHONPATH=.

pytest --cov tests --cov-report html --ds=tests.django_settings

