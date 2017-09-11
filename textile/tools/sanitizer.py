def sanitize(string):
    """
    Ensure that the text does not contain any malicious HTML code which might
    break the page.
    """
    try:
        from html5lib import parseFragment, serialize
    except ImportError:
        raise Exception("html5lib not available")

    parsed = parseFragment(string)
    clean = serialize(parsed, sanitize=True, omit_optional_tags=False,
                      quote_attr_values='always')
    return clean
