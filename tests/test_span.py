from textile import Textile

def test_span():
    t = Textile()
    result = t.span(r"hello %(bob)span *strong* and **bold**% goodbye")
    expect = ('hello <span class="bob">span <strong>strong</strong> and '
            '<b>bold</b></span> goodbye')
    assert result == expect
