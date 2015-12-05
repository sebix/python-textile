from textile import Textile

def test_image():
    t = Textile()
    result = t.image('!/imgs/myphoto.jpg!:http://jsamsa.com')
    expect = ('<a href="{0}1:url" class="img"><img alt="" src="{0}2:url" '
            '/></a>'.format(t.uid))
    assert result == expect
    assert t.refCache[1] == 'http://jsamsa.com'
    assert t.refCache[2] == '/imgs/myphoto.jpg'

    result = t.image('!</imgs/myphoto.jpg!')
    expect = '<img align="left" alt="" src="{0}3:url" />'.format(t.uid)
    assert result == expect
    assert t.refCache[3] == '/imgs/myphoto.jpg'
