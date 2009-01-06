from django.core.management.base import NoArgsCommand

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        from musicdb.classical.models import Artist
        from musicdb.classical.models import Work

        for model in (Artist, Work):
            print model
            for obj in model.objects.all():
                obj.save()
