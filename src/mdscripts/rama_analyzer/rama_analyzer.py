import itertools

import matplotlib.colors
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
from matplotlib.axes import Axes
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

from .rama_analyzer_ui import Ui_RamaAnalyzerMain
from ..io.rama_xvg import load_rama_xvg


class RamaAnalyzerMain(QtWidgets.QWidget, Ui_RamaAnalyzerMain):
    def __init__(self):
        QtWidgets.QWidget.__init__(self, None)
        self.ramachandran_data = None
        self.setupUi(self)

    def setupUi(self, RamaAnalyzerMain):
        Ui_RamaAnalyzerMain.setupUi(self, RamaAnalyzerMain)
        self.residuesListView.setEditTriggers(
            QtWidgets.QAbstractItemView.DoubleClicked | QtWidgets.QAbstractItemView.SelectedClicked)
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axes = self.figure.add_subplot(1, 1, 1)
        self.figureVerticalLayout.addWidget(self.canvas)
        self.navigationToolbar = NavigationToolbar2QT(self.canvas, self.figureWidget)
        self.figureVerticalLayout.addWidget(self.navigationToolbar)
        self.itemEditorFactory = QtWidgets.QItemEditorFactory()
        self.itemEditorFactory.registerEditor(
            QtCore.QVariant.Color,
            ColorListEditorCreator())
        QtWidgets.QItemEditorFactory.setDefaultFactory(self.itemEditorFactory)
        self.reloadPushButton.clicked.connect(self.reload)
        self.browsePushButton.clicked.connect(self.browse)
        self.stepSlider.sliderMoved.connect(self.sliderMoved)
        self.axes.axis(xmin=-180, ymin=-180, xmax=180, ymax=180)
        self.axes.set_xlabel('$\phi$ (degrees)')
        self.axes.set_ylabel('$\psi$ (degrees)')
        self.axes.vlines([0], -180, 180, colors='k', linestyles='--')
        self.axes.hlines([0], -180, 180, colors='k', linestyles='--')
        self.figure.tight_layout()
        self.canvas.draw()
        self.line = None
        self.stepByStepGroupBox.toggled.connect(self.stepByStepGroupBoxToggled)
        self.stepByStepGroupBox.setEnabled(False)
        self.playMoviePushButton.clicked.connect(self.playMovie)
        self.figurephi = Figure()
        self.canvasphi = FigureCanvasQTAgg(self.figurephi)
        self.axesphi = self.figurephi.add_subplot(1, 1, 1)
        self.figurePhiVerticalLayout = QtWidgets.QVBoxLayout(self.phiTab)
        self.figurePhiVerticalLayout.addWidget(self.canvasphi)
        self.navigationToolbarPhi = NavigationToolbar2QT(self.canvasphi, self.phiTab)
        self.figurePhiVerticalLayout.addWidget(self.navigationToolbarPhi)
        self.figurepsi = Figure()
        self.canvaspsi = FigureCanvasQTAgg(self.figurepsi)
        self.axespsi = self.figurepsi.add_subplot(1, 1, 1)
        self.figurePsiVerticalLayout = QtWidgets.QVBoxLayout(self.psiTab)
        self.figurePsiVerticalLayout.addWidget(self.canvaspsi)
        self.navigationToolbarPsi = NavigationToolbar2QT(self.canvaspsi, self.psiTab)
        self.figurePsiVerticalLayout.addWidget(self.navigationToolbarPsi)
        self.tabWidget.currentChanged.connect(self.tabSwitched)
        self.hideAllPushButton.clicked.connect(self.hideAllResidues)

    def hideAllResidues(self):
        self.residuesmodel.hideAll()

    def tabSwitched(self, index):
        if index == 0:
            self.replot()
        elif index == 1 or index == 2:
            self.plotangles()

    def plotangles(self):
        enabledresidues = [r.encode('utf-8') for r, e in zip(self.residuesmodel.residues, self.residuesmodel.enabled) if
                           e]
        for ax, what, ylabel, tabindex in [
            (self.axesphi, 'phi', '$\phi$ (degrees)', 1),
            (self.axespsi, 'psi', '$\psi$ (degrees)', 2)]:
            if self.tabWidget.currentIndex() != tabindex:
                continue
            assert isinstance(ax, Axes)
            for l in ax.lines:
                l.remove()
            ax.lines = []
            for r in enabledresidues:
                idx = self.ramachandran_data['resn'] == r
                ax.plot(self.ramachandran_data[what][idx], color=self.residuesmodel.residueColor(r),
                        label=r.decode('utf-8'))
            ax.set_xlabel('Step #')
            ax.set_ylabel(ylabel)
            ax.legend(loc='best')
            ax.grid(True, which='both')
        self.canvasphi.draw()
        self.canvaspsi.draw()

    def endMovie(self):
        self.stepByStepGroupBox.setCheckable(True)
        self.movieDelaySpinBox.setEnabled(True)
        self.stepSlider.setEnabled(True)
        self.playMoviePushButton.setText('Play')

    def playWorker(self):
        if self.playMoviePushButton.text() == 'Play':
            self.endMovie()
            return
        self.stepSlider.setValue(min(self.stepSlider.value() + self.skipFramesSpinBox.value() + 1, self.nsteps - 1))
        self.replot(self.stepSlider.value())
        if self.stepSlider.value() >= self.stepSlider.maximum():
            self.endMovie()
            return
        QtCore.QTimer.singleShot(int(self.movieDelaySpinBox.value() * 1000), self.playWorker)

    def playMovie(self):
        if self.playMoviePushButton.text() == 'Play':
            self.playMoviePushButton.setText('Stop')
            if self.stepSlider.value() >= self.stepSlider.maximum():
                self.stepSlider.triggerAction(self.stepSlider.SliderToMinimum)
            self.stepByStepGroupBox.setCheckable(False)
            self.movieDelaySpinBox.setEnabled(False)
            self.stepSlider.setEnabled(False)
            self.playWorker()
        elif self.playMoviePushButton.text() == 'Stop':
            self.playMoviePushButton.setText('Play')
        else:
            assert False

    def stepByStepGroupBoxToggled(self, on):
        if on:
            self.replot(self.stepSlider.value())
        else:
            self.replot()

    def sliderMoved(self, position):
        if not self.stepByStepGroupBox.isChecked():
            return
        else:
            self.replot(position)

    def browse(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Load an XVG file', '', '*.xvg')[0]
        print(filename)
        if filename:
            self.filenameLineEdit.setText(filename)

    def reload(self):
        filename = self.filenameLineEdit.text()
        self.load(filename)

    def load(self, filename):
        self.filenameLineEdit.setText(filename)
        self.ramachandran_data = load_rama_xvg(filename)
        self.residuesmodel = Model(sorted(set(self.ramachandran_data['resn'].tolist())))
        self.residuesListView.setModel(self.residuesmodel)
        self.residuesmodel.dataChanged.connect(lambda *args: (self.replot(), self.plotangles()))
        self.stepLabel.setText('')
        self.nsteps = np.sum(self.ramachandran_data['resn'] == self.ramachandran_data['resn'][0])
        self.nresidues = len(set(self.ramachandran_data['resn'].tolist()))
        self.stepSlider.setMinimum(0)
        self.stepSlider.setMaximum(self.nsteps - 1)
        self.stepSlider.setValue(0)
        self.stepByStepGroupBox.setEnabled(True)
        self.replot()
        self.plotangles()

    def replot(self, position=None):
        if self.tabWidget.currentIndex() != 0:
            return
        if position is None and self.stepByStepGroupBox.isChecked():
            position = self.stepSlider.value()
        assert isinstance(self.axes, Axes)
        for l in self.axes.lines:
            l.remove()
        self.axes.lines = []
        enabledresidues = [r for r, e in zip(self.residuesmodel.residues, self.residuesmodel.enabled)
                           if e]
        if position is None:
            ramachandran_data = self.ramachandran_data
        else:
            ramachandran_data = self.ramachandran_data[position * self.nresidues:(position + 1) * self.nresidues]
            self.stepLabel.setText('{:d}'.format(position))
        for i in range(len(self.residuesmodel.residues)):
            r = self.residuesmodel.residues[i]
            if r not in enabledresidues:
                continue
            idx = ramachandran_data['resn'] == r.encode('utf-8')
            self.axes.plot(ramachandran_data['phi'][idx],
                           ramachandran_data['psi'][idx], '.',
                           color=self.residuesmodel.residueColor(r), label=r)
        self.axes.legend(loc='best')
        self.canvas.draw()


class Model(QtCore.QAbstractItemModel):
    def __init__(self, residues):
        QtCore.QAbstractItemModel.__init__(self, None)
        self.residues = sorted([x.decode('utf-8') for x in residues], key=lambda x: int(x.rsplit('-', 1)[-1]))
        self.enabled = [True] * len(self.residues)
        self.colors = [None] * len(self.residues)
        for i, color in zip(range(len(self.residues)), itertools.cycle('bgrcmyk')):
            self.colors[i] = QtGui.QColor.fromRgbF(*matplotlib.colors.colorConverter.to_rgb(color))

    def columnCount(self, parent=None, *args, **kwargs):
        return 2

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.residues)

    def headerData(self, idx: int, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return ['Residue', 'Color'][idx]
        else:
            return None

    def data(self, index: QtCore.QModelIndex, role=QtCore.Qt.DisplayRole):
        assert index.row() >= 0 and index.row() < len(self.residues)
        if index.column() == 0:
            if role == QtCore.Qt.CheckStateRole:
                return [QtCore.Qt.Unchecked, QtCore.Qt.Checked][self.enabled[index.row()]]
            elif role == QtCore.Qt.DisplayRole:
                return self.residues[index.row()]
        if index.column() == 1:
            if role == QtCore.Qt.DecorationRole:
                return self.colors[index.row()]
            if role == QtCore.Qt.EditRole:
                return self.colors[index.row()]
        return None

    def setData(self, index: QtCore.QModelIndex, value=None, role=QtCore.Qt.DisplayRole):
        assert index.row() >= 0 and index.row() < len(self.residues)
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            self.enabled[index.row()] = bool(value)
            self.dataChanged.emit(self.index(index.row(), index.column()),
                                  self.index(index.row(), index.column()), [role])
            return True
        elif role == QtCore.Qt.EditRole and index.column() == 1:
            self.colors[index.row()] = value
            self.dataChanged.emit(self.index(index.row(), index.column()),
                                  self.index(index.row(), index.column()), [QtCore.Qt.DecorationRole])
        return False

    def flags(self, index: QtCore.QModelIndex):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemNeverHasChildren | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable

    def index(self, row: int, column: int, parent=None, *args, **kwargs):
        return self.createIndex(row, column)

    def parent(self, index: QtCore.QModelIndex = None):
        return QtCore.QModelIndex()

    def hideAll(self):
        self.enabled = [False] * len(self.enabled)
        self.dataChanged.emit(self.index(0, 0),
                              self.index(self.rowCount(), self.columnCount()),
                              [QtCore.Qt.CheckStateRole])

    def residueColor(self, resn):
        if isinstance(resn, bytes):
            resn = resn.decode('utf-8')
        color = [c for c, r in zip(self.colors, self.residues) if r == resn][0]
        return (color.redF(), color.greenF(), color.blueF())


class ColorListEditorCreator(QtWidgets.QItemEditorCreatorBase):
    class ColorListEditor(QtWidgets.QComboBox):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            colornames = QtGui.QColor.colorNames()
            for i in range(len(colornames)):
                self.insertItem(i, colornames[i])
                self.setItemData(i, QtGui.QColor(colornames[i]), QtCore.Qt.DecorationRole)

        @QtCore.pyqtProperty(QtGui.QColor, user=True)
        def color(self):
            return QtGui.QColor(self.currentText())

        @color.setter
        def setColor(self, color: QtGui.QColor):
            self.setCurrentIndex(self.findData(color, QtCore.Qt.DecorationRole))

    def createWidget(self, parent):
        return self.ColorListEditor(parent)
