# -*- coding: utf-8 -*-

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def duration(value):
    seconds = long(value)
    if seconds < 3600:
        return "%d′%.2d″" % (seconds / 60, seconds % 60)

    hours = seconds / 3600
    seconds = seconds % 3600
    return "%d:%.2d′%.2d″" % (hours, seconds / 60, seconds % 60)

duration.is_safe = True
