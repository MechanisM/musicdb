from django.template.defaultfilters import slugify as django_slugify

def slugify(value):
    return django_slugify(value).strip('_.- ').lower()
