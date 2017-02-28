import argparse
import os
import sys

from PyQt5 import QtWidgets

from .rtpbrowser import RTPBrowser


def run():
    p = argparse.ArgumentParser(description='Visualize residues in a GROMACS rtp file')
    p.add_argument('-f', action='store', dest='RTPFILE', type=str, help='.rtp file',
                   default='aminoacids.rtp')
    args = vars(p.parse_args())
    app = QtWidgets.QApplication([])
    mainwin = RTPBrowser()
    filename = os.path.expanduser(args['RTPFILE'])
    if os.path.exists(filename):
        mainwin.load(filename)
    mainwin.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
