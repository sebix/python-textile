def getimagesize(url):
    """
    Attempts to determine an image's width and height, and returns a string
    suitable for use in an <img> tag, or None in case of failure.
    Requires that PIL is installed.

    >>> getimagesize("http://www.google.com/intl/en_ALL/images/logo.gif")
    ... #doctest: +ELLIPSIS, +SKIP
    'width="..." height="..."'

    """

    try:
        import ImageFile
        import urllib2
    except ImportError:
        return None

    try:
        p = ImageFile.Parser()
        f = urllib2.urlopen(url)
        while True:
            s = f.read(1024)
            if not s:
                break
            p.feed(s)
            if p.image:
                return 'width="%i" height="%i"' % p.image.size
    except (IOError, ValueError):
        return None
