#!/usr/bin/env bash

until cd src
do
    echo "Waiting for volume..."
done

C_FORCE_ROOT=true exec celery worker -A firebot -l debug
