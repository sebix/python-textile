from textile import textilefactory
import pytest

def test_TextileFactory():
    f = textilefactory.TextileFactory()
    result = f.process("some text here")
    expect = '\t<p>some text here</p>'
    assert result == expect

    f = textilefactory.TextileFactory(restricted=True)
    result = f.process("more text here")
    expect = '\t<p>more text here</p>'
    assert result == expect

    # Certain parameter values are not permitted because they are illogical:

    with pytest.raises(ValueError) as ve:
        f = textilefactory.TextileFactory(lite=True)
    assert 'lite can only be enabled in restricted mode' in str(ve.value)

    with pytest.raises(ValueError) as ve:
        f = textilefactory.TextileFactory(head_offset=7)
    assert 'head_offset must be 0-6' in str(ve.value)

    with pytest.raises(ValueError) as ve:
        f = textilefactory.TextileFactory(html_type='invalid')
    assert "html_type must be 'xhtml' or 'html5'" in str(ve.value)
