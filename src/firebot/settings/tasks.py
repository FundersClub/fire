from celery.schedules import crontab
from datetime import timedelta


CELERY_BEAT_SCHEDULE = {
    ###########################################################################
    # celery
    ###########################################################################
    'celery.backend_cleanup': {
        'task': 'celery.backend_cleanup',
        'schedule': crontab(minute='0', hour='4'),
    },

    ###########################################################################
    # fb_github
    ###########################################################################
    'Look for pending repository invitations': {
        'task': 'fb_github.tasks.poll_invitations',
        'schedule': timedelta(seconds=30),
    },

}
