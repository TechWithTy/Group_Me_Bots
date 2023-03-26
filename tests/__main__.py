import pytest


def main():
    pytest.main(['-v', '--tb=long', 'tests/bots_test.py',
                'tests/posting_test.py'])


if __name__ == '__main__':
    main()
