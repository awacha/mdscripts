#!/usr/bin/env python

import os
import re
import subprocess
import sys
import tempfile

import numpy as np
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

from .gmx_extract_energy_ui import Ui_gmx_extract_energy


class CurvesModel(QtCore.QAbstractItemModel):
    # columns: name, show in left axis, show in right axis,
    def __init__(self, labels):
        super().__init__()
        self._rows = [{'name': l, 'showonleft': True, 'showonright': False, 'factor': 1.0} for l in labels]

    def columnCount(self, parent=None):
        return 4

    def data(self, index: QtCore.QModelIndex, role=None):
        row = self._rows[index.row()]
        if index.column() == 0:
            if role == QtCore.Qt.DisplayRole:
                return row['name']
            else:
                return None
        elif index.column() == 1:
            if role == QtCore.Qt.CheckStateRole:
                return [QtCore.Qt.Unchecked, QtCore.Qt.Checked][row['showonleft']]
        elif index.column() == 2:
            if role == QtCore.Qt.CheckStateRole:
                return [QtCore.Qt.Unchecked, QtCore.Qt.Checked][row['showonright']]
        elif index.column() == 3:
            if role == QtCore.Qt.DisplayRole:
                return '{:g}'.format(row['factor'])
        else:
            return None

    def flags(self, index: QtCore.QModelIndex):
        row = self._rows[index.row()]
        if index.column() == 0:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemNeverHasChildren
        if index.column() == 1 or index.column() == 2:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemNeverHasChildren | QtCore.Qt.ItemIsUserCheckable
        if index.column() == 3:
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemNeverHasChildren
        else:
            return QtCore.Qt.NoItemFlags

    def index(self, row, col, parent=None):
        return self.createIndex(row, col, None)

    def rowCount(self, parent=None):
        return len(self._rows)

    def parent(self, index: QtCore.QModelIndex = None):
        return QtCore.QModelIndex()

    def setData(self, index: QtCore.QModelIndex, newvalue, role=None):
        row = self._rows[index.row()]
        if index.column() == 1:
            row['showonleft'] = newvalue == QtCore.Qt.Checked
            self.dataChanged.emit(self.index(index.row(), 1), self.index(index.row(), 1))
            return True
        elif index.column() == 2:
            row['showonright'] = newvalue == QtCore.Qt.Checked
            self.dataChanged.emit(self.index(index.row(), 2), self.index(index.row(), 2))
            return True
        return False

    def headerData(self, column, orientation, role=None):
        if orientation != QtCore.Qt.Horizontal:
            return None
        if role == QtCore.Qt.DisplayRole:
            return ['Name', 'Left', 'Right', 'Scaling factor'][column]

    def showOnLeft(self, row):
        return self._rows[row]['showonleft']

    def showOnRight(self, row):
        return self._rows[row]['showonright']

    def factor(self, row):
        return self._rows[row]['factor']

    def hideAll(self):
        for r in self._rows:
            r['showonleft'] = r['showonright'] = False
        self.dataChanged.emit(self.index(0, 1), self.index(self.rowCount(), 2))


class MainWindow(QtWidgets.QWidget, Ui_gmx_extract_energy):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)

    def setupUi(self, Form):
        Ui_gmx_extract_energy.setupUi(self, Form)
        Form.fsmodel = QtWidgets.QFileSystemModel()
        Form.treeViewOpenFile.setModel(Form.fsmodel)
        Form.fsmodel.setNameFilters(['*.edr'])
        Form.fsmodel.setRootPath('/')
        Form.treeViewOpenFile.hideColumn(1)
        Form.treeViewOpenFile.hideColumn(2)
        Form.treeViewOpenFile.hideColumn(3)
        Form.fsmodel.sort(0, QtCore.Qt.AscendingOrder)
        Form.treeViewOpenFile.expand(Form.fsmodel.index(os.getcwd()))
        Form.treeViewOpenFile.setCurrentIndex(Form.fsmodel.index(os.getcwd()))
        Form.treeViewOpenFile.scrollTo(Form.fsmodel.index(os.getcwd()), QtWidgets.QAbstractItemView.PositionAtTop)
        Form.treeViewOpenFile.activated.connect(Form.onFileSelected)
        Form.figure = Figure()
        Form.figureCanvas = FigureCanvasQTAgg(Form.figure)
        Form.verticalLayoutFigure.addWidget(Form.figureCanvas)
        Form.navigationToolBar = NavigationToolbar2QT(Form.figureCanvas, Form)
        Form.verticalLayoutFigure.addWidget(Form.navigationToolBar)
        Form.hideAllPushButton.clicked.connect(self.hideAll)

    def onFileSelected(self, index):
        assert isinstance(self.fsmodel, QtWidgets.QFileSystemModel)
        filename = self.fsmodel.filePath(index)
        self.openFile(filename)

    def openFile(self, filename):
        self.setCurveData(*gmx_extract_energy(filename))

    def hideAll(self):
        try:
            self.curveModel.hideAll()
        except AttributeError:
            pass

    def setCurveData(self, data, labels):
        self.data = data
        self.labels = labels
        this_is_the_first_model = not hasattr(self, 'curveModel')
        self.curveModel = CurvesModel(self.labels[1:])
        self.treeViewCurves.setModel(self.curveModel)
        self.curveModel.dataChanged.connect(self.curveModelDataChanged)
        if this_is_the_first_model:
            for col in range(1, self.curveModel.columnCount()):
                self.treeViewCurves.resizeColumnToContents(col)
        self.replot()

    def curveModelDataChanged(self, idx1, idx2, roles):
        self.replot()

    def replot(self):
        assert isinstance(self.figure, Figure)
        self.figure.clear()
        axesleft = self.figure.add_subplot(1, 1, 1)
        axesleft.set_xlabel(self.labels[0])
        axesright = axesleft.twinx()
        lines = []
        labels = []
        for i in range(1, len(self.labels)):
            if self.curveModel.showOnLeft(i - 1):
                lines.append(axesleft.plot(self.data[:, 0], self.data[:, i], label=self.labels[i])[0])
                labels.append(self.labels[i])
            if self.curveModel.showOnRight(i - 1):
                lines.append(axesright.plot(self.data[:, 0], self.data[:, i], label=self.labels[i])[0])
                labels.append(self.labels[i])
        self.figure.legend(lines, labels)
        self.figureCanvas.draw()


def gmx_extract_energy(edrfile, structurefile=None, outputfile=None):
    handle = None
    if outputfile is None:
        handle, outputfile = tempfile.mkstemp('.xvg')
        os.close(handle)
    popenargs = ['gmx', 'energy', '-o', outputfile, '-f', edrfile]
    if structurefile is not None:
        popenargs.extend(['-s', structurefile])
    gmx_energy = subprocess.Popen(popenargs, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  universal_newlines=True)
    try:
        outs, errs = gmx_energy.communicate('\n'.join([str(x) for x in range(1, 100)]), timeout=2)
    except subprocess.TimeoutExpired:
        gmx_energy.kill()
        outs, errs = gmx_energy.communicate()
        raise RuntimeError('Timeout in "gmx energy"')
    assert gmx_energy.returncode is not None
    if gmx_energy.returncode:
        print(errs)
        raise RuntimeError('Nonzero exit code from "gmx energy": {}'.format(gmx_energy.returncode))
    data, labels = read_xvg(outputfile)
    if handle is not None:
        os.unlink(outputfile)
    return data, labels


def read_xvg(filename):
    data = []
    labels = ['Time (ps)']
    with open(filename, 'rt', encoding='utf-8') as f:
        while f:
            l = f.readline()
            if not l:
                break
            if l.startswith('#'):
                continue
            m = re.match('^@ s(\d+) legend "(?P<legend>.*)"$', l)
            if m:
                labels.append(m.group('legend'))
                continue
            if l.startswith('@'):
                continue
            data.append([float(x) for x in l.split()])

    return np.array(data), labels


def run():
    import argparse
    parser = argparse.ArgumentParser(description="Extract all curves from a gromacs .edr file")
    parser.add_argument('-f', action='store', type=str, help='.edr file', default='energy.edr')
    parser.add_argument('-o', action='store', type=str, help='output file', default='energy.xvg')
    parser.add_argument('-w', action='store_const', const=True, help='View results', default=False)
    parser.add_argument('-s', action='store', nargs="?", required=False, type=str,
                        help='.tpr file', const='topol.tpr', default=None)
    args = vars(parser.parse_args())

    data, labels = gmx_extract_energy(args['f'], args['s'], args['o'])
    if args["w"]:
        from PyQt5.QtWidgets import QApplication
        app = QApplication([sys.argv[0]])
        mw = MainWindow()
        mw.setCurveData(data, labels)
        mw.show()
        app.exec_()
