try:
    import regex as re
except ImportError:
    import re

try:
    # Python 3
    from urllib.parse import urlparse
    from html.parser import HTMLParser
except ImportError:
    # Python 2
    from urlparse import urlparse
    from HTMLParser import HTMLParser


def normalize_newlines(string):
    out = string.strip()
    out = re.sub(r'\r\n', '\n', out)
    out = re.sub(r'\n{3,}', '\n\n', out)
    out = re.sub(r'\n\s*\n', '\n\n', out)
    out = re.sub(r'"$', '" ', out)
    return out

def has_raw_text(text):
    """checks whether the text has text not already enclosed by a block tag"""
    # The php version has orders the below list of tags differently.  The
    # important thing to note here is that the pre must occur before the p or
    # else the regex module doesn't properly match pre-s. It only matches the
    # p in pre.
    r = re.compile(r'<(pre|p|blockquote|div|form|table|ul|ol|dl|h[1-6])[^>]*?>.*</\1>',
                   re.S).sub('', text.strip()).strip()
    r = re.compile(r'<(hr|br)[^>]*?/>').sub('', r)
    return '' != r

def list_type(list_string):
    listtypes = {
        list_string.startswith('*'): 'u',
        list_string.startswith('#'): 'o',
        (not list_string.startswith('*') and not list_string.startswith('#')):
        'd'
    }
    return listtypes.get(True, False)

def is_rel_url(url):
    """Identify relative urls."""
    (scheme, netloc) = urlparse(url)[0:2]
    return not scheme and not netloc

def encode_high(text):
    """Encode the text so that it is an appropriate HTML entity."""
    return ord(text)

def decode_high(text):
    """Decode encoded HTML entities."""
    h = HTMLParser()
    text = '&#{0};'.format(text)
    return h.unescape(text)

def encode_html(text, quotes=True):
    """Return text that's safe for an HTML attribute."""
    a = (
        ('&', '&amp;'),
        ('<', '&lt;'),
        ('>', '&gt;'))

    if quotes:
        a = a + (("'", '&#39;'),
                 ('"', '&#34;'))

    for k, v in a:
        text = text.replace(k, v)
    return text

def is_valid_url(url):
    parsed = urlparse(url)
    if parsed.scheme == '':
        return True
    return False
