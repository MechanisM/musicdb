import os

from django.conf import settings
from django.utils.hashcompat import sha_constructor
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    require_model_validation = False

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("build <role>")

        self.generate_hashes()
        self.set_role(args[0])

    def set_role(self, role):
        print "I: Setting role"

        target = os.path.join(
            settings.MYTAB_BASE_PATH, 'musicdb/settings/role.py',
        )

        open(target, 'wb').write("from roles.%s import *" % role)

        try:
            # Delete .pyc too.
            os.unlink('%sc' % target)
        except OSError:
            pass

    def generate_hashes(self):
        print "I: Generating hashes"

        hashes = {}
        static_media = os.walk(settings.STATIC_MEDIA_ROOT)

        for dirpath, _, filenames in static_media:
            commonpath = os.path.commonprefix(
                (dirpath, settings.STATIC_MEDIA_ROOT),
            )

            for filename in filenames:
                fullpath = os.path.join(dirpath, filename)
                common_path = fullpath[len(commonpath) + 1:]

                sha = sha_constructor(open(fullpath, 'rb').read())
                hashes[common_path] = sha.hexdigest()

        target = os.path.join(
            settings.MYTAB_BASE_PATH, 'musicdb/build/hashes.py',
        )

        open(target, 'wb').write("HASHES = %r" % hashes)
