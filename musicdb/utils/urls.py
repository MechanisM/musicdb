import urllib

def google_search(terms):
    return 'http://www.google.co.uk/search?%s' % urllib.urlencode({'q': terms})
