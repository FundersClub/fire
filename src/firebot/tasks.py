from __future__ import absolute_import

import time
from celery import shared_task
from logging import getLogger

LOG = getLogger(__name__)


@shared_task(bind=True)
def test_error(self):
    def f():
        raise Exception('test')
    try:
        f()
    except:
        LOG.exception('Exception log test')
    raise Exception('and an actual exception!')


@shared_task()
def long_task():
    for i in range(60):
        print(i)
        time.sleep(1)
    print('done')
