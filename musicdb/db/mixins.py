from django.db.transaction import commit_on_success

from .fields import DenormalisedCharField

__all__ = ('Mergeable',)

class Mergeable(object):

    @commit_on_success
    def merge_from(self, other):
        # Update relations
        for rel in self._meta.get_all_related_objects():
            qs = getattr(other, rel.get_accessor_name())
            qs.update(**{rel.field.name: self})

        # Delete other object
        other.delete()

        # Reset slugs
        for field, _ in self._meta.get_fields_with_model():
            if not isinstance(field, DenormalisedCharField):
                continue
            setattr(self, field.name, '')
        self.save()
