from textile import Textile

def test_encode_html():
    t = Textile()
    result = t.encode_html('''this is a "test" of text that's safe to put '''
        'in an <html> attribute.')
    expect = ('this is a &#34;test&#34; of text that&#39;s safe to put in an '
            '&lt;html&gt; attribute.')
    assert result == expect
