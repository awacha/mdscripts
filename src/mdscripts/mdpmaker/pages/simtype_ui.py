# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/mdscripts/mdpmaker/pages/simtype.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets

class Ui_WizardPage(object):
    def setupUi(self, WizardPage):
        WizardPage.setObjectName("WizardPage")
        WizardPage.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(WizardPage)
        self.verticalLayout.setObjectName("verticalLayout")
        self.typeEnergyMinimizationRadioButton = QtWidgets.QRadioButton(WizardPage)
        self.typeEnergyMinimizationRadioButton.setChecked(True)
        self.typeEnergyMinimizationRadioButton.setObjectName("typeEnergyMinimizationRadioButton")
        self.verticalLayout.addWidget(self.typeEnergyMinimizationRadioButton)
        self.typeNVTRadioButton = QtWidgets.QRadioButton(WizardPage)
        self.typeNVTRadioButton.setObjectName("typeNVTRadioButton")
        self.verticalLayout.addWidget(self.typeNVTRadioButton)
        self.typeNPTRadioButton = QtWidgets.QRadioButton(WizardPage)
        self.typeNPTRadioButton.setObjectName("typeNPTRadioButton")
        self.verticalLayout.addWidget(self.typeNPTRadioButton)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_8 = QtWidgets.QLabel(WizardPage)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout.addWidget(self.label_8)
        self.timeUnitComboBox = QtWidgets.QComboBox(WizardPage)
        self.timeUnitComboBox.setObjectName("timeUnitComboBox")
        self.timeUnitComboBox.addItem("")
        self.timeUnitComboBox.addItem("")
        self.timeUnitComboBox.addItem("")
        self.timeUnitComboBox.addItem("")
        self.horizontalLayout.addWidget(self.timeUnitComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_8.setBuddy(self.timeUnitComboBox)

        self.retranslateUi(WizardPage)
        self.timeUnitComboBox.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(WizardPage)

    def retranslateUi(self, WizardPage):
        _translate = QtCore.QCoreApplication.translate
        WizardPage.setWindowTitle(_translate("WizardPage", "WizardPage"))
        WizardPage.setTitle(_translate("WizardPage", "Type of the simulation"))
        WizardPage.setSubTitle(_translate("WizardPage", "Select the type of simulation"))
        self.typeEnergyMinimizationRadioButton.setText(_translate("WizardPage", "Energy minimi&zation"))
        self.typeNVTRadioButton.setText(_translate("WizardPage", "NV&T ensemble"))
        self.typeNPTRadioButton.setText(_translate("WizardPage", "&NPT ensemble"))
        self.label_8.setText(_translate("WizardPage", "Time unit (for display only):"))
        self.timeUnitComboBox.setItemText(0, _translate("WizardPage", "fs"))
        self.timeUnitComboBox.setItemText(1, _translate("WizardPage", "ps"))
        self.timeUnitComboBox.setItemText(2, _translate("WizardPage", "ns"))
        self.timeUnitComboBox.setItemText(3, _translate("WizardPage", "ms"))

