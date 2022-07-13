#!/usr/bin/env python3

import sys
import random
import time
import os

from PyQt5.QtCore import Qt, QEvent, QAbstractTableModel, QRect, QPoint, QObject, QThread, pyqtSignal, QSize
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

class MainWindow(QWidget):
    '''Main window of the PolyGen application'''
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.path = os.path.abspath(__file__)[:-7]

        self.initUI()

    def initUI(self):

        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)

        self.quit_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        self.quit_shortcut.activated.connect(self.exit_program)


        '''Diacid Combobox'''

        self.diacid_list = []

        for fle in sorted(os.listdir(self.path + 'XYZ/Diacids/')):
            if fle.endswith(".xyz"):
                self.diacid_list.append(fle[:-4].replace('_', ' '))

        self.diacid_lab = QLabel("Diacids")
        self.diacid_lab.setFixedWidth(100)

        self.diacid_box = QComboBox()
        self.diacid_box.addItems([str(e) for e in self.diacid_list])
        self.diacid_box.setFixedWidth(250)

        self.diacid_btn = QPushButton("Add")
        self.diacid_btn.clicked.connect(self.Add_Diacid_Chain)
        self.diacid_btn.setFixedWidth(50)

        '''Diol Combobox'''

        self.diol_list = []

        for fle in sorted(os.listdir(self.path + 'XYZ/Diols/')):
            if fle.endswith(".xyz"):
                self.diol_list.append(fle[:-4].replace('_', ' '))

        self.diol_lab = QLabel("Diols")
        self.diol_lab.setFixedWidth(100)

        self.diol_box = QComboBox()
        self.diol_box.addItems([str(e) for e in self.diol_list])
        self.diol_box.setFixedWidth(250)

        self.diol_btn = QPushButton("Add")
        self.diol_btn.clicked.connect(self.Add_Diol_Chain)
        self.diol_btn.setFixedWidth(50)


        '''Amino Acid Combobox'''

        self.amino_list = []

        for fle in sorted(os.listdir(self.path + 'XYZ/AminoAcids/')):
            if fle.endswith(".xyz"):
                self.amino_list.append(fle[:-4].replace('_', ' '))

        self.amino_lab = QLabel("Amino Acids")
        self.amino_lab.setFixedWidth(100)

        self.amino_box = QComboBox()
        self.amino_box.addItems([str(e) for e in self.amino_list])
        self.amino_box.currentIndexChanged.connect(self.Add_Amino_Chain)
        self.amino_box.setFixedWidth(250)

        self.amino_btn = QPushButton("Add")
        self.amino_btn.clicked.connect(self.Add_Amino_Chain)
        self.amino_btn.setFixedWidth(50)


        '''Sliders'''

        self.phi_val = 0

        self.phi_lab = QLabel("Phi")
        self.phi_lab.setFixedWidth(100)

        self.phi_lab2 = QLabel(str(self.phi_val))

        self.phi_slider = QSlider(Qt.Horizontal)
        self.phi_slider.setRange(-180, 180)
        self.phi_slider.setSingleStep(1)
        self.phi_slider.valueChanged.connect(self.Change_Angles)
        self.phi_slider.valueChanged.connect(self.phi_lab2.setNum)
        self.phi_slider.setFixedWidth(250)
        self.phi_slider.setValue(self.phi_val)

        self.theta_val = 90

        self.theta_lab = QLabel("Theta")
        self.theta_lab.setFixedWidth(100)

        self.theta_lab2 = QLabel(str(self.theta_val))

        self.theta_slider = QSlider(Qt.Horizontal)
        self.theta_slider.setRange(0, 180)
        self.theta_slider.setSingleStep(1)
        self.theta_slider.valueChanged.connect(self.Change_Angles)
        self.theta_slider.valueChanged.connect(self.theta_lab2.setNum)
        self.theta_slider.setFixedWidth(250)
        self.theta_slider.setValue(self.theta_val)

        '''Plot'''

        #self.poly_plot = PlotCurve(self)
        #self.poly_plot_tb = NavigationToolbar2QT(self.poly_plot, self)

        '''Grid Layout'''

        dash_count = 70

        row=0
        self.grid_layout.addWidget(self.diacid_lab, row, 0, 1, 1, alignment=Qt.AlignCenter)
        self.grid_layout.addWidget(self.diacid_box, row, 1, 1, 1, alignment=Qt.AlignCenter)
        self.grid_layout.addWidget(self.diacid_btn, row, 2, 1, 1, alignment=Qt.AlignCenter)
        
        row+=1
        self.grid_layout.addWidget(self.diol_lab, row, 0, 1, 1, alignment=Qt.AlignCenter)
        self.grid_layout.addWidget(self.diol_box, row, 1, 1, 1, alignment=Qt.AlignCenter)
        self.grid_layout.addWidget(self.diol_btn, row, 2, 1, 1, alignment=Qt.AlignCenter)
        
        row+=1
        self.grid_layout.addWidget(self.amino_lab, row, 0, 1, 1, alignment=Qt.AlignCenter)
        self.grid_layout.addWidget(self.amino_box, row, 1, 1, 1, alignment=Qt.AlignCenter)
        self.grid_layout.addWidget(self.amino_btn, row, 2, 1, 1, alignment=Qt.AlignCenter)

        row+=1
        self.grid_layout.addWidget(QLabel(" -"*dash_count), row, 0, 1, 3, alignment=Qt.AlignCenter)

        row+=1
        self.grid_layout.addWidget(self.phi_lab, row, 0, 1, 1, alignment=Qt.AlignCenter)
        self.grid_layout.addWidget(self.phi_slider, row, 1, 1, 1, alignment=Qt.AlignCenter)
        self.grid_layout.addWidget(self.phi_lab2, row, 2, 1, 1, alignment=Qt.AlignCenter)

        row+=1
        self.grid_layout.addWidget(self.theta_lab, row, 0, 1, 1, alignment=Qt.AlignCenter)
        self.grid_layout.addWidget(self.theta_slider, row, 1, 1, 1, alignment=Qt.AlignCenter)
        self.grid_layout.addWidget(self.theta_lab2, row, 2, 1, 1, alignment=Qt.AlignCenter)

        row+=1
        self.grid_layout.addWidget(QLabel(" -"*dash_count), row, 0, 1, 3, alignment=Qt.AlignCenter)

        row+=1
        #self.grid_layout.addWidget(self.poly_plot, row, 0, 3, 3)
        
        row+=3
        #self.grid_layout.addWidget(self.poly_plot_tb, row, 0, 1, 3, alignment=Qt.AlignCenter)

        return


    def Add_Diacid_Chain(self):
        self

    def Add_Diol_Chain(self):
        self

    def Add_Amino_Chain(self):
        self
    
    def Change_Angles(self):
        self.phi_val = self.phi_slider.value()
        self.theta_val = self.theta_slider.value()

    def Update_Plot(self):
        self
    
    def exit_program(selaf):
        '''Function used to exit the program and close all windows'''
        exit()

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec_()
    win.destroy()

if __name__ == '__main__':
    sys.exit(main())

