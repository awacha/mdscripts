import sys

from PyQt5 import QtWidgets

from .mdpmaker import MDPWizard


def run():
    app = QtWidgets.QApplication([])
    mainwin = MDPWizard()
    mainwin.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()
