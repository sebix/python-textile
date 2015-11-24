from textile import Textile

def test_table():
    t = Textile()
    result = t.table('(rowclass). |one|two|three|\n|a|b|c|')
    expect = '\t<table>\n\t\t<tr class="rowclass">\n\t\t\t<td>one</td>\n\t\t\t<td>two</td>\n\t\t\t<td>three</td>\n\t\t</tr>\n\t\t<tr>\n\t\t\t<td>a</td>\n\t\t\t<td>b</td>\n\t\t\t<td>c</td>\n\t\t</tr>\n\t</table>\n\n'
    assert result == expect
