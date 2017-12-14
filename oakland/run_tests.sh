#!/bin/sh

export PYTHONPATH=.

py.test --cov=oakland --cov-report html --ds=tests.django_settings

