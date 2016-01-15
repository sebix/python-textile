try:
    import regex as re
except ImportError:
    import re


def normalize_newlines(string):
    out = string.strip()
    out = re.sub(r'\r\n', '\n', out)
    out = re.sub(r'\n{3,}', '\n\n', out)
    out = re.sub(r'\n\s*\n', '\n\n', out)
    out = re.sub(r'"$', '" ', out)
    return out

def hasRawText(text):
    """checks whether the text has text not already enclosed by a block tag"""
    # The php version has orders the below list of tags differently.  The
    # important thing to note here is that the pre must occur before the p or
    # else the regex module doesn't properly match pre-s. It only matches the
    # p in pre.
    r = re.compile(r'<(pre|p|blockquote|div|form|table|ul|ol|dl|h[1-6])[^>]*?>.*</\1>',
                   re.S).sub('', text.strip()).strip()
    r = re.compile(r'<(hr|br)[^>]*?/>').sub('', r)
    return '' != r

