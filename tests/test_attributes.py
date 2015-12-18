from textile import Textile
import re

def test_parse_attributes():
    t = Textile()
    assert t.parse_attributes('\\1', element='td') == {'colspan': '1'}
    assert t.parse_attributes('/1', element='td') == {'rowspan': '1'}
    assert t.parse_attributes('^', element='td') == {'style': 'vertical-align:top;'}
    assert t.parse_attributes('{color: blue}') == {'style': 'color: blue;'}
    assert t.parse_attributes('[en]') == {'lang': 'en'}
    assert t.parse_attributes('(cssclass)') == {'class': 'cssclass'}
    assert t.parse_attributes('(') == {'style': 'padding-left:1em;'}
    assert t.parse_attributes(')') == {'style': 'padding-right:1em;'}
    assert t.parse_attributes('<') == {'style': 'text-align:left;'}
    assert t.parse_attributes('(c#i)') == {'class': 'c', 'id': 'i'}
    assert t.parse_attributes('\\2 100', element='col') == {'span': '2', 'width': '100'}
