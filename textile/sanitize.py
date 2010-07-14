import html5lib
from html5lib import sanitizer, serializer


def sanitize(string, html_type):
    try:
        import html5lib
        from html5lib import sanitizer
    except ImportError:
        raise Exception("html5lib not available")
        
    p = html5lib.HTMLParser(tokenizer=sanitizer.HTMLSanitizer)
    tree = p.parseFragment(string)
    
    walker = treewalkers.getTreeWalker("dom")
    stream = walker(tree)

    if html_type = 'xhtml':
        s = serializer.htmlserializer.XHTMLSerializer()
    else:
        s = serializer.htmlserializer.HTMLSerializer()
    return s.render(stream)
