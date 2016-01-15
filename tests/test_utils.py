from textile import utils

def test_has_raw_text():
    assert utils.hasRawText('<p>foo bar biz baz</p>') is False
    assert utils.hasRawText(' why yes, yes it does') is True
