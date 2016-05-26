import subprocess

def test_console_script():
    result = subprocess.check_output(['python', '-m', 'textile', 'README.textile'])
    with open('tests/fixtures/README.txt') as f:
        expect = ''.join(f.readlines())
    assert result == expect
