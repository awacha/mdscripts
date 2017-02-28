import re

import graphviz
from PyQt5 import QtWidgets, QtSvg, QtGui

from .rtpbrowser_ui import Ui_Form


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
        self.engineComboBox.addItems(['dot', 'neato', 'twopi', 'circo', 'fdp', 'sfdp', 'patchwork'])
        self.engineComboBox.setCurrentIndex(1)
        self.residueComboBox.currentIndexChanged.connect(self.onPlotClicked)
        self.engineComboBox.currentIndexChanged.connect(self.onPlotClicked)
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
        lastcaption = None
        with open(filename, 'rt', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('['):
                    caption = line.replace('[', '').replace(']', '').strip()
                    if caption == 'bondedtypes':
                        continue
                    elif caption == 'atoms':
                        self._residues[-1]['atoms'] = []
                    elif caption == 'bonds':
                        self._residues[-1]['bonds'] = []
                    elif caption in ['angles', 'impropers', 'dihedrals', 'cmap']:
                        pass
                    else:
                        self._residues.append({'name': caption})
                    lastcaption = caption
                elif not line.strip():
                    continue
                elif lastcaption == 'atoms':
                    name, type_, charge, cgroup = line.strip().split()
                    self._residues[-1]['atoms'].append(Atom(name, type_, float(charge), int(cgroup)))
                elif lastcaption == 'bonds':
                    first, last = line.strip().split()[:2]
                    self._residues[-1]['bonds'].append((first, last))
                else:
                    pass
        self.residueComboBox.clear()
        self.residueComboBox.addItems(sorted([r['name'] for r in self._residues]))
        self.residueComboBox.setCurrentIndex(0)

    def onBrowse(self):
        filename, filter = QtWidgets.QFileDialog.getOpenFileName(self, "Open Residue Topology Parameter file",
                                                                 filter="*.rtp", initialFilter="*.rtp")
        if filename:
            self.load(filename)

    def onPlotClicked(self):
        residue = [r for r in self._residues if r['name'] == self.residueComboBox.currentText()][0]
        graph = graphviz.Graph(residue['name'], 'Residue {}'.format(residue['name']), format='svg',
                               engine=self.engineComboBox.currentText())
        for atom in residue['atoms']:
            graph.node(atom.name)
        for first, last in residue['bonds']:
            graph.edge(first, last)
        svgdata = graph.pipe(format='svg')
        svgdata = re.sub(b'font-size="\d+.\d+"', 'font-size="{}"'.format(self.fontSizeSpinBox.value()).encode('utf-8'),
                         svgdata)
        # graph.render()
        self.svgWidget.load(svgdata)
        self.svgWidget.setFont(QtGui.QFont('sans', 1200))
