import re

from django.db.models import fields

from musicdb.utils import slugify

__all__ = ('DenormalisedCharField', 'MySlugField', 'FirstLetterField', \
    'DirNameField')

class DenormalisedCharField(fields.CharField):
    def __init__(self, attr, *args, **kwargs):
        # Set a longer max_length by default
        kwargs['max_length'] = kwargs.get('max_length', 100)
        kwargs['db_index'] = kwargs.get('db_index', True)
        kwargs['editable'] = kwargs.get('editable', False)
        super(DenormalisedCharField, self).__init__(*args, **kwargs)

        self.attr = attr

    def pre_save(self, obj, add):
        val = getattr(obj, self.attr)

        if callable(val):
            val = val()

        return val[:self.max_length]

class MySlugField(DenormalisedCharField):
    def __init__(self, *args, **kwargs):
        self.filter = None
        if 'filter' in kwargs:
            self.filter = kwargs.pop('filter')

        super(MySlugField, self).__init__(*args, **kwargs)

    def pre_save(self, obj, add):
        val = super(MySlugField, self).pre_save(obj, add)
        val = slugify(val)[:self.max_length]

        count = 1
        val_to_prepend = val[:self.max_length - 3]

        if self.filter is not None:
            qs = getattr(obj, self.filter)()
        else:
            qs = obj.__class__.objects.all()

        while count <= 999:
            filters = {
                self.name: val,
            }

            if qs.filter(**filters).exclude(pk=obj.pk).count() == 0:
                return val

            val = "%s-%d" % (val_to_prepend, count)
            count += 1

        assert False

class FirstLetterField(DenormalisedCharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 1
        super(FirstLetterField, self).__init__(*args, **kwargs)

    def pre_save(self, obj, add):
        val = super(FirstLetterField, self).pre_save(obj, add).lower()

        if re.match('[a-z]', val):
            return val
        elif re.match('\d', val):
            return '0'
        else:
            return '-'

class DirNameField(DenormalisedCharField):
    def pre_save(self, obj, add):
        val = super(DirNameField, self).pre_save(obj, add)
        return val.replace('/', '-')
