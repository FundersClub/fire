import os
import subprocess
import sys

from django.conf import settings
from django.test import TestCase


class TestFlake8(TestCase):
    def testFlake8(self):
        flake8 = os.path.abspath(os.path.join(
            os.path.dirname(sys.executable),
            'flake8',
        ))
        if not os.path.exists(flake8):
            raise Exception('Missing flake8 at "{}"'.format(flake8))

        try:
            subprocess.check_output([flake8, settings.BASE_DIR])
        except subprocess.CalledProcessError as e:
            raise Exception(e.output.decode('utf-8'))
