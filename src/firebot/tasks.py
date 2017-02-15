from __future__ import absolute_import
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
