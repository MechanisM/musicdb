import urllib

def google_search(terms):
    q = terms.encode('utf8') # urlencode doesn't like unicode strings
    return 'http://www.google.co.uk/search?%s' % urllib.urlencode({'q': q})
