import networkx
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT, FigureCanvasQTAgg
from matplotlib.figure import Figure

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
        self.previous_pos=None
        self.previous_residue = None

    def setupUi(self, Form):
        Ui_Form.setupUi(self, Form)
        self.browsePushButton.clicked.connect(self.onBrowse)
        self.residueComboBox.currentIndexChanged.connect(self.onPlotClicked)
        self.optDistanceDoubleSpinBox.valueChanged.connect(self.onPlotClicked)
        self.labelComboBox.currentIndexChanged.connect(self.onPlotClicked)
        self.plotPushButton.clicked.connect(self.onPlotClicked)
        self.scaleDoubleSpinBox.valueChanged.connect(self.onPlotClicked)
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout = self.layout()
        assert isinstance(layout, QtWidgets.QVBoxLayout)
        layout.addWidget(self.canvas)
        self.figuretoolbar = NavigationToolbar2QT(self.canvas, self)
        layout.addWidget(self.figuretoolbar)
        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.canvas.setObjectName('canvas')
        self.axes = self.figure.add_subplot(1,1,1)

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
        self.previous_residue = None
        self.previous_pos = None
        self.plot()

    def plot(self):
        residue = [r for r in self._residues if r.name == self.residueComboBox.currentText()][0]
        assert isinstance(residue, ResidueTopology)
        if residue.name != self.previous_residue:
            self.previous_pos = None
            self.previous_residue = residue.name
        graph = networkx.Graph()
        labels = {}
        colors = []
        colordict = {'H':'lightgray','C':'green','N':'blue', 'O':'red', 'S':'yellow', 'P':'purple'}
        for atom in residue.atoms:
            graph.add_node(atom[0])
            labels[atom[0]]=atom[self.labelComboBox.currentIndex()]
        for first, last in residue.bonds:
            graph.add_edge(first, last)
            for at in [first, last]:
                if at not in labels:
                    labels[at] = at
        for at in graph.nodes():
            try:
                if at[0] in '+-':
                    element = at[1]
                else:
                    element = at[0]
                colors.append(colordict[element])
            except KeyError:
                colors.append('darkgray')
        self.axes.cla()
        if self.previous_pos is None:

            self.previous_pos = networkx.spring_layout(
                graph,
                scale=self.scaleDoubleSpinBox.value(),
                k=self.optDistanceDoubleSpinBox.value(),
#                pos=networkx.spectral_layout(graph),
                iterations=500)

        networkx.draw(
            graph,
            pos = self.previous_pos,
            labels=labels,
            ax=self.axes,
            with_labels=True,
            node_color=colors)
        self.canvas.draw()
