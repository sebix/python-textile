import textile

def test_github_issue_17():
    result = textile.textile('!http://www.ox.ac.uk/favicon.ico!')
    expect = '\t<p><img alt="" src="http://www.ox.ac.uk/favicon.ico" /></p>'
    assert result == expect
