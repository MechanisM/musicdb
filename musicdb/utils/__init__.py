from django.template.defaultfilters import slugify as django_slugify

def slugify(value):
    value = django_slugify(value)
    return value.strip('_.- ').lower()
