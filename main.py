from os import system
from models import Execute

def get_data():
    Execute.init_selenium()
    Execute.get_organic()
    Execute.get_local()
    Execute.get_ads()
    Execute.get_related()

if __name__ == '__main__':
    system('cls')
    get_data()
    print("End of __main__")