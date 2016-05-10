from textile import Textile

def test_getRefs():
    t = Textile()
    result = t.getRefs("some text [Google]http://www.google.com")
    expect = 'some text '
    assert result == expect

    result = t.urlrefs
    expect = {'Google': 'http://www.google.com'}
    assert result == expect
