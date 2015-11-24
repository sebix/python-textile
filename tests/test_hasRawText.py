from textile import Textile
def test_has_raw_text():
    t = Textile()
    assert t.hasRawText('<p>foo bar biz baz</p>') is False
    assert t.hasRawText(' why yes, yes it does') is True
