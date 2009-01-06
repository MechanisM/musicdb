import re

def slugify(txt):
    txt = re.sub('\s+', '-', txt)
    txt = re.sub('[^\w-]', '', txt)
    return txt.strip('_.- ').lower()
