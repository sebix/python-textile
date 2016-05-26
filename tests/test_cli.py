import six
import subprocess

def test_console_script():
    command = ['python', '-m', 'textile', 'README.textile']
    try:
        result = subprocess.check_output(command)
    except AttributeError:
        result = subprocess.Popen(command,
                stdout=subprocess.PIPE).communicate()[0]
    with open('tests/fixtures/README.txt') as f:
        expect = ''.join(f.readlines())
    assert six.text_type(result) == six.text_type(expect)
