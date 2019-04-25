# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/mdscripts/mdpmaker/pages/ewald.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(WizardPage)
        self.gridLayout.setObjectName("gridLayout")
        self.label_40 = QtWidgets.QLabel(WizardPage)
        self.label_40.setObjectName("label_40")
        self.gridLayout.addWidget(self.label_40, 0, 0, 1, 1)
        self.fourierspacingDoubleSpinBox = QtWidgets.QDoubleSpinBox(WizardPage)
        self.fourierspacingDoubleSpinBox.setDecimals(4)
        self.fourierspacingDoubleSpinBox.setMaximum(999999999.0)
        self.fourierspacingDoubleSpinBox.setProperty("value", 0.12)
        self.fourierspacingDoubleSpinBox.setObjectName("fourierspacingDoubleSpinBox")
        self.gridLayout.addWidget(self.fourierspacingDoubleSpinBox, 0, 1, 1, 1)
        self.label_41 = QtWidgets.QLabel(WizardPage)
        self.label_41.setObjectName("label_41")
        self.gridLayout.addWidget(self.label_41, 1, 0, 1, 1)
        self.pme_orderSpinBox = QtWidgets.QSpinBox(WizardPage)
        self.pme_orderSpinBox.setProperty("value", 4)
        self.pme_orderSpinBox.setObjectName("pme_orderSpinBox")
        self.gridLayout.addWidget(self.pme_orderSpinBox, 1, 1, 1, 1)
        self.line = QtWidgets.QFrame(WizardPage)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 2, 0, 1, 2)
        self.label_56 = QtWidgets.QLabel(WizardPage)
        self.label_56.setObjectName("label_56")
        self.gridLayout.addWidget(self.label_56, 3, 0, 1, 1)
        self.constraintsComboBox = QtWidgets.QComboBox(WizardPage)
        self.constraintsComboBox.setObjectName("constraintsComboBox")
        self.constraintsComboBox.addItem("")
        self.constraintsComboBox.addItem("")
        self.constraintsComboBox.addItem("")
        self.constraintsComboBox.addItem("")
        self.constraintsComboBox.addItem("")
        self.gridLayout.addWidget(self.constraintsComboBox, 3, 1, 1, 1)
        self.label_57 = QtWidgets.QLabel(WizardPage)
        self.label_57.setObjectName("label_57")
        self.gridLayout.addWidget(self.label_57, 4, 0, 1, 1)
        self.label_58 = QtWidgets.QLabel(WizardPage)
        self.label_58.setObjectName("label_58")
        self.gridLayout.addWidget(self.label_58, 4, 1, 1, 1)
        self.label_59 = QtWidgets.QLabel(WizardPage)
        self.label_59.setObjectName("label_59")
        self.gridLayout.addWidget(self.label_59, 5, 0, 1, 1)
        self.lincs_orderSpinBox = QtWidgets.QSpinBox(WizardPage)
        self.lincs_orderSpinBox.setProperty("value", 4)
        self.lincs_orderSpinBox.setObjectName("lincs_orderSpinBox")
        self.gridLayout.addWidget(self.lincs_orderSpinBox, 5, 1, 1, 1)
        self.label_60 = QtWidgets.QLabel(WizardPage)
        self.label_60.setObjectName("label_60")
        self.gridLayout.addWidget(self.label_60, 6, 0, 1, 1)
        self.lincs_iterSpinBox = QtWidgets.QSpinBox(WizardPage)
        self.lincs_iterSpinBox.setMinimum(1)
        self.lincs_iterSpinBox.setObjectName("lincs_iterSpinBox")
        self.gridLayout.addWidget(self.lincs_iterSpinBox, 6, 1, 1, 1)
        self.label_61 = QtWidgets.QLabel(WizardPage)
        self.label_61.setObjectName("label_61")
        self.gridLayout.addWidget(self.label_61, 7, 0, 1, 1)
        self.lincs_warnangleDoubleSpinBox = QtWidgets.QDoubleSpinBox(WizardPage)
        self.lincs_warnangleDoubleSpinBox.setMaximum(360.0)
        self.lincs_warnangleDoubleSpinBox.setProperty("value", 30.0)
        self.lincs_warnangleDoubleSpinBox.setObjectName("lincs_warnangleDoubleSpinBox")
        self.gridLayout.addWidget(self.lincs_warnangleDoubleSpinBox, 7, 1, 1, 1)
        self.label_40.setBuddy(self.fourierspacingDoubleSpinBox)
        self.label_41.setBuddy(self.pme_orderSpinBox)
        self.label_56.setBuddy(self.constraintsComboBox)
        self.label_59.setBuddy(self.lincs_orderSpinBox)
        self.label_60.setBuddy(self.lincs_iterSpinBox)
        self.label_61.setBuddy(self.lincs_warnangleDoubleSpinBox)

        self.retranslateUi(WizardPage)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        _translate = QtCore.QCoreApplication.translate
        WizardPage.setWindowTitle(_translate("WizardPage", "WizardPage"))
        WizardPage.setTitle(_translate("WizardPage", "Ewald & Constraints"))
        WizardPage.setSubTitle(_translate("WizardPage", "Settings for Ewald summation and bond constraint algorithms"))
        self.label_40.setText(_translate("WizardPage", "Fourier spacing [nm]:"))
        self.label_41.setText(_translate("WizardPage", "PME interpolation order:"))
        self.label_56.setText(_translate("WizardPage", "Apply constraints to:"))
        self.constraintsComboBox.setItemText(0, _translate("WizardPage", "none"))
        self.constraintsComboBox.setItemText(1, _translate("WizardPage", "h-bonds"))
        self.constraintsComboBox.setItemText(2, _translate("WizardPage", "all-bonds"))
        self.constraintsComboBox.setItemText(3, _translate("WizardPage", "h-angles"))
        self.constraintsComboBox.setItemText(4, _translate("WizardPage", "all-angles"))
        self.label_57.setText(_translate("WizardPage", "Constraint algorithm:"))
        self.label_58.setText(_translate("WizardPage", "LINCS"))
        self.label_59.setText(_translate("WizardPage", "LINCS order:"))
        self.label_60.setText(_translate("WizardPage", "Numbr of LINCS iterations:"))
        self.label_61.setText(_translate("WizardPage", "LINCS warning angle threshold [deg]:"))

