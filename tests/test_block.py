from textile import Textile

def test_block():
    t = Textile()
    result = t.block('h1. foobar baby')
    expect = '\t<h1>foobar baby</h1>'
    assert result == expect

    result = t.fBlock("bq", "", None, "", "Hello BlockQuote")
    expect = ('\t<blockquote>\n', '\t\t<p>', 'Hello BlockQuote', '</p>',
            '\n\t</blockquote>', False)
    assert result == expect

    result = t.fBlock("bq", "", None, "http://google.com", "Hello BlockQuote")
    expect = ('\t<blockquote cite="http://google.com">\n', '\t\t<p>',
            'Hello BlockQuote', '</p>', '\n\t</blockquote>', False)
    assert result == expect

    result = t.fBlock("bc", "", None, "", 'printf "Hello, World";')
    # the content of text will be turned shelved, so we'll asert only the
    # deterministic portions of the expected values, below
    expect = ('<pre>', '<code>', 'printf "Hello, World";', '</code>', '</pre>', False)
    assert result[0:2] == expect[0:2]
    assert result[3:] == expect[3:]

    result = t.fBlock("h1", "", None, "", "foobar")
    expect = ('', '\t<h1>', 'foobar', '</h1>', '', False)
    assert result == expect
