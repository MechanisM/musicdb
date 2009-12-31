from django.db.models import Q
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

class NextPreviousMixin(object):
    def _get_next_or_previous(self, next, **kwargs):
        fields = []
        operator = []

        for field in list(self._meta.ordering) + ['pk']:
            if field.startswith('-'):
                field = field[1:]
                op = next and 'lt' or 'gt'
            else:
                op = next and 'gt' or 'lt'

            if getattr(self, field) is None:
                continue

            fields.append(field)
            operator.append(op)

        # Construct Q such that any of:
        #
        #  (f_1 > self.f_1)
        #  (f_2 > self.f_2) & (f_1 = self.f_1)
        #  (f_3 > self.f_3) & (f_2 = self.f_2) & (f_1 = self.f_1)
        # ...
        #  (f_n > self.f_n) & (f_[n-1] = self.f_[n-1]) & ... & (f_1 = self.f_1)
        #
        # is true, replacing '>' where appropriate.
        q = Q()
        for idx in range(len(fields)):
            inner = Q(**{'%s__%s' % (fields[idx], operator[idx]): \
                getattr(self, fields[idx]),
            })
            for other in reversed(fields[:idx]):
                inner &= Q(**{other: getattr(self, other)})
            q |= inner

        qs = self.__class__._default_manager.filter(**kwargs).filter(q)

        if not next:
            qs = qs.reverse()

        try:
            return qs[0]
        except IndexError:
            return None

    def next(self, **kwargs):
        return self._get_next_or_previous(next=True, **kwargs)

    def previous(self, **kwargs):
        return self._get_next_or_previous(next=False, **kwargs)
