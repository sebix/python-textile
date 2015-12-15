from textile import Textile
import re

def test_urls():
    t = Textile()
    assert t.isRelURL("http://www.google.com/") is False
    assert t.isRelURL("/foo") is True

    assert t.relURL("http://www.google.com/") == 'http://www.google.com/'

    result = t.links('fooobar "Google":http://google.com/foobar/ and hello world "flickr":http://flickr.com/photos/jsamsa/ ')
    expect = 'fooobar {0}2:shelve and hello world {0}4:shelve '.format(t.uid)
    assert result == expect

    result = t.links('""Open the door, HAL!"":https://xkcd.com/375/')
    expect = '{0}6:shelve'.format(t.uid)
    assert result == expect

    result = t.links('"$":http://domain.tld/test_[brackets]')
    expect = '{0}8:shelve'.format(t.uid)
    assert result == expect

    result = t.links('<em>"$":http://domain.tld/test_</em>')
    expect = '<em>{0}10:shelve</em>'.format(t.uid)
    assert result == expect

def test_rel_attribute():
    t = Textile(rel='nofollow')
    result = t.parse('"$":http://domain.tld')
    expect = '\t<p><a href="http://domain.tld" rel="nofollow">domain.tld</a></p>'
    assert result == expect
