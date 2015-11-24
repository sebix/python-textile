from textile import Textile

def test_urls():
    t = Textile()
    assert t.isRelURL("http://www.google.com/") is False
    assert t.isRelURL("/foo") is True

    assert t.relURL("http://www.google.com/") == 'http://www.google.com/'

    assert t.autoLink("http://www.ya.ru") == '"$":http://www.ya.ru'
