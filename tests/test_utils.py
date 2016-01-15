from textile import utils

def test_encode_html():
    result = utils.encode_html('''this is a "test" of text that's safe to '''
            'put in an <html> attribute.')
    expect = ('this is a &#34;test&#34; of text that&#39;s safe to put in an '
            '&lt;html&gt; attribute.')
    assert result == expect

def test_has_raw_text():
    assert utils.has_raw_text('<p>foo bar biz baz</p>') is False
    assert utils.has_raw_text(' why yes, yes it does') is True

def test_is_rel_url():
    assert utils.is_rel_url("http://www.google.com/") is False
    assert utils.is_rel_url("/foo") is True
