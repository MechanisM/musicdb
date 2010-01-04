import os
import re

def track_names_from_filenames(filenames, capitalise=True):
    filenames = [os.path.basename(x) for x in filenames]
    filenames = [re.sub('\.[^\.]+$', '', x) for x in filenames]
    filenames = [re.sub('^[\d_\-]+', '', x) for x in filenames]
    filenames = [x.replace('[', '(') for x in filenames]
    filenames = [x.replace(']', ')') for x in filenames]

    common_prefix = os.path.commonprefix(filenames)
    filenames = [x[len(common_prefix):] for x in filenames]

    reverse_filenames = [x[::-1] for x in filenames]
    common_suffix = os.path.commonprefix(reverse_filenames)
    if len(common_suffix) >= 3:
        filenames = [x[:-len(common_suffix)] for x in filenames]

    filenames = [re.sub('^[\d_\.\-\s]+', '', x) for x in filenames]
    filenames = [re.sub('^[VI]+\.\s*', '', x) for x in filenames]
    filenames = [re.sub('[_\s]+', ' ', x) for x in filenames]

    filenames = [x or '(unknown)' for x in filenames]
    filenames = [x[0].capitalize() + x[1:] for x in filenames]
    filenames = [re.sub(r'\b- ', ': ', x) for x in filenames]

    filenames = [re.sub('\s+\((19|20)\d\d\)$', '', x) for x in filenames]

    if capitalise:
        print "capital idea"
        re_capital = re.compile(r'(^|\s|\()(\w)')
        rep = lambda m: '%s%s' % (m.group(1), m.group(2).upper())
        filenames = [re_capital.sub(rep, x) for x in filenames]

    return filenames
