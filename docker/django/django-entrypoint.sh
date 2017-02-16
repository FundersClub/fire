#!/usr/bin/env bash

until cd src
do
    echo "Waiting for django volume..."
done

python manage.py runserver 0.0.0.0:12000 --settings=firebot.settings.dev --noreload
