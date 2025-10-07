#!/bin/sh

set -xe

celery -A main.celery worker --loglevel=info
