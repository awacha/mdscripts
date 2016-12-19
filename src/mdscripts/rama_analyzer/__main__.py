import os
import sys

from PyQt5 import QtWidgets

from .rama_analyzer import RamaAnalyzerMain


def run():
    app = QtWidgets.QApplication(sys.argv)
    mainwin = RamaAnalyzerMain()
    if len(sys.argv) > 1:
        filename = os.path.expanduser(sys.argv[1])
        if os.path.exists(filename):
            mainwin.load(filename)
    mainwin.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
