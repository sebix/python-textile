from textile import Textile

def test_block():
    t = Textile()
    result = t.block('h1. foobar baby')
    expect = '\t<h1>foobar baby</h1>'
    assert result == expect
