from __future__ import unicode_literals
from textile import Textile
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

def test_block():
    t = Textile()
    result = t.block('h1. foobar baby')
    expect = '\t<h1>foobar baby</h1>'
    assert result == expect

    result = t.fBlock("bq", "", None, "", "Hello BlockQuote")
    expect = ('blockquote', OrderedDict(), 'p', OrderedDict(),
            'Hello BlockQuote', False)
    assert result == expect

    result = t.fBlock("bq", "", None, "http://google.com", "Hello BlockQuote")
    citation = '{0}1:url'.format(t.uid)
    expect = ('blockquote', OrderedDict([('cite',
        '{0.uid}{0.refIndex}:url'.format(t))]), 'p', OrderedDict(),
        'Hello BlockQuote', False)
    assert result == expect

    result = t.fBlock("bc", "", None, "", 'printf "Hello, World";')
    # the content of text will be turned shelved, so we'll asert only the
    # deterministic portions of the expected values, below
    expect = ('pre', OrderedDict(), 'code', OrderedDict(), 'shelve', False)
    assert result[0:3] == expect[0:3]
    assert result[-1] == expect[-1]

    result = t.fBlock("h1", "", None, "", "foobar")
    expect = ('h1', OrderedDict(), '', OrderedDict(), 'foobar', False)
    assert result == expect

def test_block_tags_false():
    t = Textile(block_tags=False)
    assert t.block_tags is False

    result = t.parse('test')
    expect = 'test'
    assert result == expect
