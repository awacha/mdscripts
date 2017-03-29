import re

import graphviz
from PyQt5 import QtWidgets, QtSvg, QtGui

from .rtpbrowser_ui import Ui_Form
from ..core import ResidueTopology


class Atom(object):
    def __init__(self, atomname, atomtype, charge, cgroup):
        self.name = atomname
        self.atomtype = atomtype
        self.charge = charge
        self.cgroup = cgroup

class RTPBrowser(QtWidgets.QWidget, Ui_Form):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.show()

    def setupUi(self, Form):
        Ui_Form.setupUi(self, Form)
        self.browsePushButton.clicked.connect(self.onBrowse)
        self.residueComboBox.currentIndexChanged.connect(self.onPlotClicked)
        self.engineComboBox.currentIndexChanged.connect(self.onPlotClicked)
        self.labelComboBox.currentIndexChanged.connect(self.onPlotClicked)
        self.plotPushButton.clicked.connect(self.onPlotClicked)
        self.fontSizeSpinBox.valueChanged.connect(self.onPlotClicked)
        self.svgWidget = QtSvg.QSvgWidget(self)
        layout = self.layout()
        assert isinstance(layout, QtWidgets.QVBoxLayout)
        layout.addWidget(self.svgWidget)
        self.svgWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.svgWidget.setObjectName('svgWidget')

    def load(self, filename):
        self.filenameLineEdit.setText(filename)
        self._residues = []
        self._residues = list(ResidueTopology.load(filename))
        self.residueComboBox.clear()
        self.residueComboBox.addItems(sorted([r.name for r in self._residues]))
        self.residueComboBox.setCurrentIndex(0)

    def onBrowse(self):
        filename, filter = QtWidgets.QFileDialog.getOpenFileName(self, "Open Residue Topology Parameter file",
                                                                 filter="*.rtp", initialFilter="*.rtp")
        if filename:
            self.load(filename)

    def onPlotClicked(self):
        residue = [r for r in self._residues if r.name == self.residueComboBox.currentText()][0]
        assert isinstance(residue, ResidueTopology)
        graph = graphviz.Graph(residue.name, 'Residue {}'.format(residue.name), format='svg',
                               engine=self.engineComboBox.currentText())
        for atom in residue.atoms:
            graph.node(atom[0], label = atom[self.labelComboBox.currentIndex()])
        for first, last in residue.bonds:
            graph.edge(first, last)
        svgdata = graph.pipe(format='svg')
        svgdata = re.sub(b'font-size="\d+.\d+"', 'font-size="{}"'.format(self.fontSizeSpinBox.value()).encode('utf-8'),
                         svgdata)
        # graph.render()
        self.svgWidget.load(svgdata)
        self.svgWidget.setFont(QtGui.QFont('sans', 1200))
