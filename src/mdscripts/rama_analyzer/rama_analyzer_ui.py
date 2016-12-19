# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/mdscripts/rama_analyzer/rama_analyzer.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets


class Ui_RamaAnalyzerMain(object):
    def setupUi(self, RamaAnalyzerMain):
        RamaAnalyzerMain.setObjectName("RamaAnalyzerMain")
        RamaAnalyzerMain.resize(594, 451)
        self.verticalLayout = QtWidgets.QVBoxLayout(RamaAnalyzerMain)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(RamaAnalyzerMain)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.widget = QtWidgets.QWidget(self.splitter)
        self.widget.setObjectName("widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame = QtWidgets.QFrame(self.widget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.filenameLineEdit = QtWidgets.QLineEdit(self.frame)
        self.filenameLineEdit.setObjectName("filenameLineEdit")
        self.gridLayout.addWidget(self.filenameLineEdit, 0, 0, 1, 1)
        self.browsePushButton = QtWidgets.QPushButton(self.frame)
        self.browsePushButton.setObjectName("browsePushButton")
        self.gridLayout.addWidget(self.browsePushButton, 0, 1, 1, 1)
        self.reloadPushButton = QtWidgets.QPushButton(self.frame)
        self.reloadPushButton.setObjectName("reloadPushButton")
        self.gridLayout.addWidget(self.reloadPushButton, 1, 0, 1, 2)
        self.verticalLayout_2.addWidget(self.frame)
        self.residuesListView = QtWidgets.QListView(self.widget)
        self.residuesListView.setObjectName("residuesListView")
        self.verticalLayout_2.addWidget(self.residuesListView)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.tabWidget = QtWidgets.QTabWidget(self.splitter)
        self.tabWidget.setObjectName("tabWidget")
        self.tabRamachandran = QtWidgets.QWidget()
        self.tabRamachandran.setObjectName("tabRamachandran")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.tabRamachandran)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.rightWidget = QtWidgets.QWidget(self.tabRamachandran)
        self.rightWidget.setObjectName("rightWidget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.rightWidget)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.widget_2 = QtWidgets.QWidget(self.rightWidget)
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget_2)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.stepByStepGroupBox = QtWidgets.QGroupBox(self.widget_2)
        self.stepByStepGroupBox.setCheckable(True)
        self.stepByStepGroupBox.setChecked(True)
        self.stepByStepGroupBox.setObjectName("stepByStepGroupBox")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.stepByStepGroupBox)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.widget_3 = QtWidgets.QWidget(self.stepByStepGroupBox)
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.widget_3)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.stepSlider = QtWidgets.QSlider(self.widget_3)
        self.stepSlider.setOrientation(QtCore.Qt.Horizontal)
        self.stepSlider.setInvertedControls(False)
        self.stepSlider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.stepSlider.setObjectName("stepSlider")
        self.horizontalLayout.addWidget(self.stepSlider)
        self.stepLabel = QtWidgets.QLabel(self.widget_3)
        self.stepLabel.setObjectName("stepLabel")
        self.horizontalLayout.addWidget(self.stepLabel)
        self.verticalLayout_6.addWidget(self.widget_3)
        self.widget_4 = QtWidgets.QWidget(self.stepByStepGroupBox)
        self.widget_4.setObjectName("widget_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_4)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.widget_4)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.movieDelaySpinBox = QtWidgets.QDoubleSpinBox(self.widget_4)
        self.movieDelaySpinBox.setProperty("value", 0.0)
        self.movieDelaySpinBox.setObjectName("movieDelaySpinBox")
        self.horizontalLayout_2.addWidget(self.movieDelaySpinBox)
        self.label_3 = QtWidgets.QLabel(self.widget_4)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.skipFramesSpinBox = QtWidgets.QSpinBox(self.widget_4)
        self.skipFramesSpinBox.setObjectName("skipFramesSpinBox")
        self.horizontalLayout_2.addWidget(self.skipFramesSpinBox)
        self.playMoviePushButton = QtWidgets.QPushButton(self.widget_4)
        self.playMoviePushButton.setObjectName("playMoviePushButton")
        self.horizontalLayout_2.addWidget(self.playMoviePushButton)
        self.verticalLayout_6.addWidget(self.widget_4)
        self.verticalLayout_3.addWidget(self.stepByStepGroupBox)
        self.verticalLayout_4.addWidget(self.widget_2)
        self.figureWidget = QtWidgets.QWidget(self.rightWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.figureWidget.sizePolicy().hasHeightForWidth())
        self.figureWidget.setSizePolicy(sizePolicy)
        self.figureWidget.setObjectName("figureWidget")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.figureWidget)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.figureVerticalLayout = QtWidgets.QVBoxLayout()
        self.figureVerticalLayout.setObjectName("figureVerticalLayout")
        self.verticalLayout_5.addLayout(self.figureVerticalLayout)
        self.verticalLayout_4.addWidget(self.figureWidget)
        self.verticalLayout_7.addWidget(self.rightWidget)
        self.tabWidget.addTab(self.tabRamachandran, "")
        self.phiTab = QtWidgets.QWidget()
        self.phiTab.setObjectName("phiTab")
        self.tabWidget.addTab(self.phiTab, "")
        self.psiTab = QtWidgets.QWidget()
        self.psiTab.setObjectName("psiTab")
        self.tabWidget.addTab(self.psiTab, "")
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(RamaAnalyzerMain)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(RamaAnalyzerMain)

    def retranslateUi(self, RamaAnalyzerMain):
        _translate = QtCore.QCoreApplication.translate
        RamaAnalyzerMain.setWindowTitle(_translate("RamaAnalyzerMain", "Ramachandran Plot Analyzer"))
        self.browsePushButton.setText(_translate("RamaAnalyzerMain", "Browse"))
        self.reloadPushButton.setText(_translate("RamaAnalyzerMain", "(Re)load"))
        self.stepByStepGroupBox.setTitle(_translate("RamaAnalyzerMain", "Step-by-step view"))
        self.label.setText(_translate("RamaAnalyzerMain", "Step:"))
        self.stepLabel.setText(_translate("RamaAnalyzerMain", "N/A"))
        self.label_2.setText(_translate("RamaAnalyzerMain", "Movie delay:"))
        self.label_3.setText(_translate("RamaAnalyzerMain", "Skip frames:"))
        self.playMoviePushButton.setText(_translate("RamaAnalyzerMain", "Play"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabRamachandran),
                                  _translate("RamaAnalyzerMain", "Ramachandran plot"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.phiTab), _translate("RamaAnalyzerMain", "Phi"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.psiTab), _translate("RamaAnalyzerMain", "Psi"))
