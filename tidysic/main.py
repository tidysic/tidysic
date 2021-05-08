from tidysic.tidysic import Tidysic

def run() -> None:
    tidysic = Tidysic('tests/music', 'result')
    tidysic.run()


if __name__ == '__main__':
    run()
