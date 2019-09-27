#!/usr/bin/env python

import os
import re
import subprocess
import sys
import tempfile

import numpy as np
import scipy.signal
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

from .extract_energy_ui import Ui_gmx_extract_energy


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
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemNeverHasChildren | QtCore.Qt.ItemIsSelectable
        if index.column() == 1 or index.column() == 2:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemNeverHasChildren | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsSelectable
        if index.column() == 3:
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemNeverHasChildren | QtCore.Qt.ItemIsSelectable
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


class StatisticsModel(QtCore.QAbstractItemModel):
    # columns: name, mean, median, trend, std, std (pcnt), ptp, ptp (pcnt),
    def __init__(self, data, labels, tmin=None, tmax=None):
        super().__init__()
        self.data = data
        self.labels = labels
        if tmin is None:
            tmin = data[:, 0].min()
        if tmax is None:
            tmax = data[:, 0].max()
        self.tmin = tmin
        self.tmax = tmax

    def columnCount(self, parent=None):
        return 8

    def data(self, index: QtCore.QModelIndex, role=None):
        datacolumn = index.row() + 1
        dataidx = np.logical_and(self.data[:, 0] >= self.tmin, self.data[:, 0] <= self.tmax)
        data = self.data[dataidx, datacolumn]
        if role != QtCore.Qt.DisplayRole:
            return None
        if index.column() == 0:
            return self.labels[datacolumn]
        elif index.column() == 1:
            return str(np.mean(data))
        elif index.column() == 2:
            return str(np.median(data))
        elif index.column() == 3:
            coeffs = np.polyfit(self.data[dataidx, 0], data, 1)
            return str(coeffs[0])
        elif index.column() == 4:
            return str(np.std(data))
        elif index.column() == 5:
            return str(np.std(data) / np.mean(data) * 100)
        elif index.column() == 6:
            return str(np.ptp(data))
        elif index.column() == 7:
            return str(np.ptp(data) / np.mean(data) * 100)
        else:
            return None

    def flags(self, index: QtCore.QModelIndex):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemNeverHasChildren | QtCore.Qt.ItemIsSelectable

    def index(self, row, col, parent=None):
        return self.createIndex(row, col, None)

    def rowCount(self, parent=None):
        return self.data.shape[1] - 1

    def parent(self, index: QtCore.QModelIndex = None):
        return QtCore.QModelIndex()

    def headerData(self, column, orientation, role=None):
        if orientation != QtCore.Qt.Horizontal:
            return None
        if role == QtCore.Qt.DisplayRole:
            return ['Name', 'Mean', 'Median', 'Trend', 'STD', 'STD %', 'P2P', 'P2P %'][column]

    def setTmin(self, value):
        self.tmin = value
        self.dataChanged.emit(self.index(0, 1), self.index(self.rowCount(), self.columnCount()),
                              [QtCore.Qt.DisplayRole])

    def setTmax(self, value):
        self.tmax = value
        self.dataChanged.emit(self.index(0, 1), self.index(self.rowCount(), self.columnCount()),
                              [QtCore.Qt.DisplayRole])


class MainWindow(QtWidgets.QWidget, Ui_gmx_extract_energy):
    windowfunctions = {'barthann': 'Bartlett-Hann',
                       'bartlett': 'Bartlett',
                       'blackman': 'Blackman',
                       'blackmanharris': 'Blackman-Harris',
                       'bohman': 'Bohman',
                       'boxcar': 'Rectangular',
                       'cosine': 'Cosine',
                       'flattop': 'Flat top',
                       'hamming': 'Hamming',
                       'hann': 'Hann',
                       'nuttall': 'Nuttall',
                       'parzen': 'Parzen',
                       'triang': 'Triangular',
                       'tukey': 'Tukey (tapered cosine)',
                       }

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.cursor = None
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
        Form.hideAllPushButton.clicked.connect(Form.hideAll)
        Form.toolButtonGoFirst.clicked.connect(
            lambda: Form.horizontalSliderCursor.triggerAction(Form.horizontalSliderCursor.SliderToMinimum))
        Form.toolButtonGoLast.clicked.connect(
            lambda: Form.horizontalSliderCursor.triggerAction(Form.horizontalSliderCursor.SliderToMaximum))
        Form.toolButtonGoNext.clicked.connect(
            lambda: Form.horizontalSliderCursor.triggerAction(Form.horizontalSliderCursor.SliderSingleStepAdd))
        Form.toolButtonGoPrevious.clicked.connect(
            lambda: Form.horizontalSliderCursor.triggerAction(Form.horizontalSliderCursor.SliderSingleStepSub))
        Form.tminSlider.valueChanged.connect(Form.onTminSliderValueChanged)
        Form.tmaxSlider.valueChanged.connect(Form.onTmaxSliderValueChanged)
        Form.smoothingSlider.valueChanged.connect(Form.onSmoothingChanged)
        index = 0
        for i, w in enumerate(sorted(self.windowfunctions)):
            Form.smoothingFunctionComboBox.addItem(self.windowfunctions[w])
            if w == 'boxcar':
                index = i
        Form.smoothingFunctionComboBox.setCurrentIndex(index)
        Form.smoothingFunctionComboBox.currentIndexChanged.connect(lambda *args: self.replot())

    def onSmoothingChanged(self, smoothing):
        self.replot()

    def onFileSelected(self, index):
        assert isinstance(self.fsmodel, QtWidgets.QFileSystemModel)
        filename = self.fsmodel.filePath(index)
        self.openFile(filename)

    def openFile(self, filename):
        self.setCurveData(*extract_energy(filename))

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
        self.statModel = StatisticsModel(self.data, self.labels)
        self.statisticsTreeView.setModel(self.statModel)
        if this_is_the_first_model:
            for col in range(1, self.curveModel.columnCount()):
                self.treeViewCurves.resizeColumnToContents(col)
            for col in range(1, self.statModel.columnCount()):
                self.statisticsTreeView.resizeColumnToContents(col)
        self.setScalerLimits()
        self.replot()

    def setScalerLimits(self):
        self.horizontalSliderCursor.setMinimum(0)
        self.horizontalSliderCursor.setMaximum(self.data.shape[0] - 1)
        self.tminSlider.setMinimum(0)
        self.tminSlider.setMaximum(self.data.shape[0] - 1)
        self.tmaxSlider.setMinimum(0)
        self.tmaxSlider.setMaximum(self.data.shape[0] - 1)
        self.tmaxSlider.setValue(self.data.shape[0] - 1)
        self.tminSlider.setValue(0)
        self.tminSpinBox.setMinimum(self.data[0, 0])
        self.tminSpinBox.setMaximum(self.data[-1, 0])
        self.tmaxSpinBox.setMinimum(self.data[0, 0])
        self.tmaxSpinBox.setMaximum(self.data[-1, 0])
        self.smoothingSlider.setMinimum(0)
        self.smoothingSlider.setMaximum(int(np.floor(0.5 * (self.data.shape[0] - 1))))

    def onTminSliderValueChanged(self, value):
        if value > self.tmaxSlider.value():
            self.tminSlider.setValue(self.tmaxSlider.value())
        self.tminSpinBox.setValue(self.cursorposToTime(self.tminSlider.value()))
        self.statModel.setTmin(self.cursorposToTime(self.tminSlider.value()))

    def cursorposToTime(self, cursorpos):
        return self.data[:, 0][cursorpos]

    def timeToCursorpos(self, time):
        return np.searchsorted(self.data[:, 0], time, side='right')

    def onTmaxSliderValueChanged(self, value):
        if value < self.tminSlider.value():
            self.tmaxSlider.setValue(self.tminSlider.value())
        self.tmaxSpinBox.setValue(self.cursorposToTime(self.tmaxSlider.value()))
        self.statModel.setTmax(self.cursorposToTime(self.tmaxSlider.value()))

    def curveModelDataChanged(self, idx1, idx2, roles):
        self.replot()

    def smoothingWindowName(self):
        return [k for k in self.windowfunctions
                if self.windowfunctions[k] == self.smoothingFunctionComboBox.currentText()][0]


    def replot(self):
        smoothing = 2 * self.smoothingSlider.value() + 1
        if smoothing < 3:
            smoothing = None
        assert isinstance(self.figure, Figure)
        self.figure.clear()
        axesleft = self.figure.add_subplot(1, 1, 1)
        axesleft.set_xlabel(self.labels[0])
        axesright = axesleft.twinx()
        lines = []
        labels = []
        for i in range(1, len(self.labels)):
            if smoothing is not None:
                window = scipy.signal.get_window(self.smoothingWindowName(), smoothing)
                curve = scipy.signal.fftconvolve(self.data[:, i], window, 'valid') / window.sum()
                # smoothing = 2*n+1. Cut n points from both the left and the right side of x.
                n = (smoothing - 1) // 2
                x = self.data[n:-n, 0]
            else:
                curve = self.data[:, i]
                x = self.data[:, 0]
            if self.curveModel.showOnLeft(i - 1):
                lines.append(axesleft.plot(x, curve, label=self.labels[i])[0])
                labels.append(self.labels[i])
            if self.curveModel.showOnRight(i - 1):
                lines.append(axesright.plot(x, curve, label=self.labels[i])[0])
                labels.append(self.labels[i])
        self.figure.legend(lines, labels)
        self.figureCanvas.draw()


def extract_energy(edrfile, structurefile=None, outputfile=None):
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
        outs, errs = gmx_energy.communicate('\n'.join([str(x) for x in range(1, 100)]), timeout=200)
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

    data, labels = extract_energy(args['f'], args['s'], args['o'])
    if args["w"]:
        from PyQt5.QtWidgets import QApplication
        app = QApplication([sys.argv[0]])
        mw = MainWindow()
        mw.setCurveData(data, labels)
        mw.show()
        app.exec_()
