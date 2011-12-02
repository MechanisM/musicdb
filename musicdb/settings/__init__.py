import sys

from defaults import *

if sys.argv[1:2] == ['test']:
    from roles.test import *
else:
    from role import *

    try:
        from custom import *
    except ImportError:
        pass

STATIC_URL = STATIC_MEDIA_URL % {
    'hash': 'hash',
    'path': '',
}
