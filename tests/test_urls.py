from textile import Textile

def test_urls():
    t = Textile()
    assert t.isRelURL("http://www.google.com/") is False
    assert t.isRelURL("/foo") is True

    assert t.relURL("http://www.google.com/") == 'http://www.google.com/'

    assert t.autoLink("http://www.ya.ru") == '"$":http://www.ya.ru'

    result = t.links('fooobar "Google":http://google.com/foobar/ and hello world "flickr":http://flickr.com/photos/jsamsa/ ')
    expect = re.compile(r'fooobar [a-f0-9]{32} and hello world [a-f0-9]{32}')
    assert expect.search(result) is not None
