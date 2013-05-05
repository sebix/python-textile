def getimagesize(url):
    """
    Attempts to determine an image's width and height, and returns a tuple,
    (width, height), in pixels or an empty string in case of failure.
    Requires that PIL is installed.

    >>> getimagesize("http://www.google.com/intl/en_ALL/images/logo.gif")
    (276, 110)
    >>> getimagesize("http://bad.domain/")
    ''
    """

    try:
        from PIL import ImageFile
    except ImportError:
        return ''

    try:
        from urllib.request import urlopen
    except (ImportError):
        from urllib2 import urlopen

    try:
        p = ImageFile.Parser()
        f = urlopen(url)
        while True:
            s = f.read(1024)
            if not s:
                break
            p.feed(s)
            if p.image:
                return p.image.size
    except (IOError, ValueError):
        return ''


def setup_module(module):
    from nose.plugins.skip import SkipTest
    try:
        __import__('PIL')
    except ImportError:
        raise SkipTest()
