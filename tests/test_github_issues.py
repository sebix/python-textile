import textile

def test_github_issue_17():
    result = textile.textile('!http://www.ox.ac.uk/favicon.ico!')
    expect = '\t<p><img alt="" src="http://www.ox.ac.uk/favicon.ico" /></p>'
    assert result == expect

def test_github_issue_20():
    text = 'This is a link to a ["Wikipedia article about Textile":http://en.wikipedia.org/wiki/Textile_(markup_language)].'
    result = textile.textile(text)
    expect = '\t<p>This is a link to a <a href="http://en.wikipedia.org/wiki/Textile_%28markup_language%29">Wikipedia article about Textile</a>.</p>'
    assert result == expect
