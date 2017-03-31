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
    # fb_emails
    ###########################################################################
    'Sanitize old emails': {
        'task': 'fb_emails.tasks.sanitize_old_emails',
        'schedule': crontab(minute='0', hour='10'),  # 3AM PST
    },

    ###########################################################################
    # fb_github
    ###########################################################################
    'Look for pending repository invitations': {
        'task': 'fb_github.tasks.poll_invitations',
        'schedule': timedelta(seconds=15),
    },

    'Sanitize old issues': {
        'task': 'fb_github.tasks.sanitize_old_issues',
        'schedule': crontab(minute='0', hour='10'),  # 3AM PST
    },

}
