"""
Utilities needed for making doctests compatible with both Py2 and Py3.

Author: Radek Czajka <radekczajka@nowoczesnapolska.org.pl>
"""

from __future__ import unicode_literals
import sys

if sys.version_info[0] < 3:
    import copy

    class Py3Wrapper(object):
        '''
        You can have Python 2 and 3 compatible Unicode-aware code
        without 'u' prefixes (unsupported in Python 3.2) using
        __future__.unicode_literals, but any doctests expecting strings
        will fail in Python 2, because unicode.__repr__ still adds
        a prefix anyway, and bytes.__repr__ doesn't.

        >>> from doctest import run_docstring_examples
        >>> def sad_doctest():
        ...     """
        ...     >>> (b'tuple', 'of', (3, 'things'))
        ...     (b'tuple', 'of', (3, 'things'))
        ...     """
        ...     pass
        >>> run_docstring_examples(sad_doctest, globals())  # doctest: +ELLIPSIS
        ***************...
        Got:
            ('tuple', u'of', (3, u'things'))...

        This class provides a workaround for this issue. 'Shifting'
        an object to Py3 (which is an instance of this class) creates
        a deep copy of it, with all unicode and bytes objects wrapped
        in a class providing a Py3-compatbile __repr__.

        >>> Py3 << (b'tuple', 'of', (3, 'things'))
        (b'tuple', 'of', (3, 'things'))

        '''
        class Py3WrappingMemo(dict):
            """
            The copy.deepcopy function uses one optional argument, which
            is a `memo` dict, used internally as an object cache.
            Normally, deepcopy creates this dict for itself, but we're
            going to use it to modify the behaviour of deepcopy to wrap
            all the unicode and str objects with our wrapper classes.

            This way, deepcopy still behaves as expected if not
            explicitly passed an instance of this class.

            """
            class Py3Unicode(unicode):
                """Wrapper for unicode objects."""
                def __repr__(self):
                    return unicode.__repr__(self)[1:]

            class Py3Str(str):
                """Wrapper for str objects."""
                def __repr__(self):
                    return 'b' + str.__repr__(self)

            # We're meddling with copy.deepcopy internals here.
            # However, iIf deepcopy isn't explicitly passed an instance
            # of this class as `memo`, the only thing this meddling
            # causes is a dict lookup for each unicode and str copied.
            copy._deepcopy_dispatch[unicode] = lambda x, memo: memo.get(x, x)
            copy._deepcopy_dispatch[str] = lambda x, memo: memo.get(x, x)
            copy._deepcopy_dispatch[Py3Unicode] = copy._deepcopy_atomic
            copy._deepcopy_dispatch[Py3Str] = copy._deepcopy_atomic

            def get(self, item, default=None):
                """Actual wrapping happens here."""
                if type(item) is unicode:
                    return self.Py3Unicode(item)
                elif type(item) is str:
                    return self.Py3Str(item)
                else:
                    return dict.get(self, item, default)

        def __lshift__(self, obj):
            return copy.deepcopy(obj, memo=self.Py3WrappingMemo())

else:
    class Py3Wrapper(object):
        """Under Python 3, that's a no-op."""
        def __lshift__(self, obj):
            return obj


Py3 = Py3Wrapper()
