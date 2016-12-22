import argparse
import os
import sys

from PyQt5 import QtWidgets

from .rama_analyzer import RamaAnalyzerMain


def run():
    p = argparse.ArgumentParser(description='Analyze Ramachandran plots of Gromacs trajectories')
    p.add_argument('-f', action='store', dest='XVGFILE', type=str, help='.xvg file produced by gmx rama',
                   default='rama.xvg')
    args = vars(p.parse_args())
    app = QtWidgets.QApplication([])
    mainwin = RamaAnalyzerMain()
    filename = os.path.expanduser(args['XVGFILE'])
    if os.path.exists(filename):
        mainwin.load(filename)
    mainwin.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
