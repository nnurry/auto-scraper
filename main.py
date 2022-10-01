from os import system
from models import Execute
from sys import argv
from const import HTML_PATH


def get_data():
    Execute.get_organic()
    Execute.get_local()
    Execute.get_ads()
    Execute.get_related()

if __name__ == '__main__':
    system('cls')
    get_data(HTML_PATH if len(argv) == 1 else argv[1])
    print("End of __main__")