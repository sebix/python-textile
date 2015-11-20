from textile.tools.imagesize import getimagesize

def test_imagesize():
    assert getimagesize("http://www.google.com/intl/en_ALL/images/logo.gif") == (276, 110)
    assert getimagesize("http://bad.domain/") == ''
    assert getimagesize("http://www.google.com/robots.txt") is None
