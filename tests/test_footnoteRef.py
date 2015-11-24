from textile import Textile
import re

def test_footnoteRef():
    t = Textile()
    result = t.footnoteRef('foo[1] ')
    expect_pattern = r'foo<sup class="footnote" id="fnrev([a-f0-9]{32})"><a href="#fn\1">1</a></sup> '
    assert re.compile(expect_pattern).search(result) is not None
