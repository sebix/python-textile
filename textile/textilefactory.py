from __future__ import unicode_literals
from .core import Textile


class TextileFactory(object):
    """ Use TextileFactory to create a Textile object which can be re-used to
    process multiple strings with the same settings."""

    def __init__(self, restricted=False, lite=False, sanitize=False,
                 noimage=None, auto_link=False, get_sizes=False,
                 head_offset=0, html_type='xhtml'):

        self.class_parms = {}
        self.method_parms = {}

        if lite and not restricted:
            raise ValueError("lite can only be enabled in restricted mode")

        if restricted:
            self.class_parms['restricted'] = True
            self.class_parms['lite'] = lite
            self.method_parms['rel'] = 'nofollow'

        if noimage is None:
            if restricted:
                noimage = True
            else:
                noimage = False

        self.class_parms['noimage'] = noimage
        self.method_parms['sanitize'] = sanitize
        self.class_parms['auto_link'] = auto_link
        self.class_parms['get_sizes'] = get_sizes

        if int(head_offset) not in range(0, 6):
            raise ValueError("head_offset must be 0-6")
        else:
            self.method_parms['head_offset'] = head_offset

        if html_type not in ['xhtml', 'html5']:
            raise ValueError("html_type must be 'xhtml' or 'html5'")
        else:
            self.class_parms['html_type'] = html_type

    def process(self, text):
        return Textile(**self.class_parms).parse(text, **self.method_parms)
