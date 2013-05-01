def sanitize(string):
    """
    >>> sanitize("\\t<p>a paragraph</p>")
    u'\\t<p>a paragraph</p>'

    >>> sanitize("\\t<script>alert('evil script');</script>")
    u"\\t&lt;script&gt;alert('evil script');&lt;/script&gt;"

    """
    try:
        import html5lib
        from html5lib import sanitizer, serializer, treewalkers
    except ImportError:
        raise Exception("html5lib not available")

    p = html5lib.HTMLParser(tokenizer=sanitizer.HTMLSanitizer)
    tree = p.parseFragment(string)

    walker = treewalkers.getTreeWalker("simpletree")
    stream = walker(tree)

    s = serializer.htmlserializer.HTMLSerializer(omit_optional_tags=False,
            quote_attr_values=True)
    return s.render(stream)


def setup_module(module):
    from nose.plugins.skip import SkipTest
    try:
        import html5lib
    except ImportError:
        raise SkipTest()
