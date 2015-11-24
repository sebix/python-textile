from textile import Textile

def test_image():
    t = Textile()
    result = t.image('!/imgs/myphoto.jpg!:http://jsamsa.com')
    expect = ('<a href="http://jsamsa.com" class="img"><img alt="" '
            'src="/imgs/myphoto.jpg" /></a>')
    assert result == expect

    result = t.image('!</imgs/myphoto.jpg!')
    expect = '<img align="left" alt="" src="/imgs/myphoto.jpg" />'
    assert result == expect
