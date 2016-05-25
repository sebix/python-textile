from __future__ import unicode_literals

import textile
from textile.objects import Block

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

def test_block():
    t = textile.Textile()
    result = t.block('h1. foobar baby')
    expect = '\t<h1>foobar baby</h1>'
    assert result == expect

    b = Block(t, "bq", "", None, "", "Hello BlockQuote")
    expect = ('blockquote', OrderedDict(), 'p', OrderedDict(),
            'Hello BlockQuote')
    result = (b.outer_tag, b.outer_atts, b.inner_tag, b.inner_atts, b.content)
    assert result == expect

    b = Block(t, "bq", "", None, "http://google.com", "Hello BlockQuote")
    citation = '{0}1:url'.format(t.uid)
    expect = ('blockquote', OrderedDict([('cite',
        '{0.uid}{0.refIndex}:url'.format(t))]), 'p', OrderedDict(),
        'Hello BlockQuote')
    result = (b.outer_tag, b.outer_atts, b.inner_tag, b.inner_atts, b.content)
    assert result == expect

    b = Block(t, "bc", "", None, "", 'printf "Hello, World";')
    # the content of text will be turned shelved, so we'll asert only the
    # deterministic portions of the expected values, below
    expect = ('pre', OrderedDict(), 'code', OrderedDict())
    result = (b.outer_tag, b.outer_atts, b.inner_tag, b.inner_atts)
    assert result == expect

    b = Block(t, "h1", "", None, "", "foobar")
    expect = ('h1', OrderedDict(), '', OrderedDict(), 'foobar')
    result = (b.outer_tag, b.outer_atts, b.inner_tag, b.inner_atts, b.content)
    assert result == expect

def test_block_tags_false():
    t = textile.Textile(block_tags=False)
    assert t.block_tags is False

    result = t.parse('test')
    expect = 'test'
    assert result == expect

def test_blockcode_extended():
    input = 'bc.. text\nmoretext\n\nevenmoretext\n\nmoremoretext\n\np. test'
    expect = '<pre><code>text\nmoretext\n\nevenmoretext\n\nmoremoretext</code></pre>\n\n\t<p>test</p>'
    t = textile.Textile()
    result = t.parse(input)
    assert result == expect

def test_blockcode_in_README():
    with open('README.textile') as f:
        readme = ''.join(f.readlines())
    result = textile.textile(readme)
    expect = """	<p><a href="https://travis-ci.org/textile/python-textile"><img alt="" src="https://travis-ci.org/textile/python-textile.svg" /></a> <a href="https://coveralls.io/github/textile/python-textile?branch=master"><img alt="" src="https://coveralls.io/repos/github/textile/python-textile/badge.svg" /></a> <a href="https://codecov.io/github/textile/python-textile"><img alt="" src="https://codecov.io/github/textile/python-textile/coverage.svg" /></a></p>

	<h1>python-textile</h1>

	<p>python-textile is a Python port of <a href="http://txstyle.org/">Textile</a>, Dean Allen&#8217;s humane web text generator.</p>

	<h2>Installation</h2>

	<p><code>pip install textile</code></p>

	<p>Optional dependencies include:
	<ul>
		<li><a href="http://python-pillow.github.io/"><span class="caps">PIL</span>/Pillow</a> (for checking images size)</li>
		<li><a href="https://pypi.python.org/pypi/regex">regex</a> (for faster unicode-aware string matching).</li>
	</ul></p>

	<h2>Usage</h2>

<pre><code>import textile
&gt;&gt;&gt; s = &quot;&quot;&quot;
... _This_ is a *test.*
...
... * One
... * Two
... * Three
...
... Link to &quot;Slashdot&quot;:http://slashdot.org/
... &quot;&quot;&quot;
&gt;&gt;&gt; html = textile.textile(s)
&gt;&gt;&gt; print html
	&lt;p&gt;&lt;em&gt;This&lt;/em&gt; is a &lt;strong&gt;test.&lt;/strong&gt;&lt;/p&gt;

	&lt;ul&gt;
		&lt;li&gt;One&lt;/li&gt;
		&lt;li&gt;Two&lt;/li&gt;
		&lt;li&gt;Three&lt;/li&gt;
	&lt;/ul&gt;

	&lt;p&gt;Link to &lt;a href=&quot;http://slashdot.org/&quot;&gt;Slashdot&lt;/a&gt;&lt;/p&gt;
&gt;&gt;&gt;</code></pre>

	<h3>Notes:</h3>

	<ul>
		<li>Active development supports Python 2.6 or later (including Python 3.2+).</li>
	</ul>"""
    assert result == expect
