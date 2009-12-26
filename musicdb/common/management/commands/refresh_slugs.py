from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        from musicdb.classical.models import Artist, Work, Recording

        for model in (Artist, Work, Recording):
            print model
            for obj in model.objects.all():
                obj.save()
