#!/usr/bin/python

import sys

from os.path import join, dirname, abspath

sys.path.insert(0, dirname(dirname(abspath(__file__))))
sys.path.insert(0, join(dirname(dirname(abspath(__file__))), 'contrib'))

from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    raise

if __name__ == "__main__":
    execute_manager(settings)
