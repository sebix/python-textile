def sanitize(string):
    """
    Ensure that the text does not contain any malicious HTML code which might
    break the page.
    """
    try:
        import html5lib
        from html5lib import sanitizer, serializer, treewalkers
    except ImportError:
        raise Exception("html5lib not available")

    p = html5lib.HTMLParser(tokenizer=sanitizer.HTMLSanitizer)
    tree = p.parseFragment(string)

    walker = treewalkers.getTreeWalker("etree")
    stream = walker(tree)

    s = serializer.htmlserializer.HTMLSerializer(omit_optional_tags=False,
            quote_attr_values=True)
    return s.render(stream)
