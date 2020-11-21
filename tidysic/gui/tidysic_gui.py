from PyQt5 import QtWidgets

from tidysic.gui import TidysicWindow


def run():

    app = QtWidgets.QApplication([])

    main_window = TidysicWindow()
    main_window.show()

    app.exec()


if __name__ == '__main__':

    run()
