#!/usr/bin/env python3

import sys
import random
import time
import os
import numpy as np
import re

from pathlib import Path

from PyQt5.QtCore import Qt, QEvent, QAbstractTableModel, QRect, QPoint, QObject, QThread, pyqtSignal, QSize
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from mpl_toolkits.mplot3d import axes3d

class MainWindow(QWidget):
    '''Main window of the PolyGen application'''
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.path = os.path.abspath(__file__)[:-7]

        self.atom_colors = {'c' : 'black', 
                            'h' : 'gray', 
                            'o' : 'red', 
                            'n' : 'blue',
                            'x' : 'white'
                            }

        self.atom_size = {'c' : 0.732,
                          'h' : 0.315,
                          'o' : 0.662,
                          'n' : 0.711,
                          'x' : 0.001
                          }

        self.bond_distance = 1.10

        self.new_molecule_dict = {'atoms' : ['x'], 
                                  'coords' : np.zeros((1,3))
                                  }

        self.bonds = []

        self.initUI()

    def initUI(self):

        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)

        self.quit_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        self.quit_shortcut.activated.connect(self.exit_program)


        '''Diacid Combobox'''

        self.diacid_list = []

        for fle in sorted(os.listdir(Path(self.path + 'XYZ/Diacids/'))):
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

        for fle in sorted(os.listdir(Path(self.path + 'XYZ/Diols/'))):
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

        for fle in sorted(os.listdir(Path(self.path + 'XYZ/AminoAcids/'))):
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

        self.fig = Figure()
        self.canvas = FigureCanvasQTAgg(self.fig)

        self.ax = self.canvas.figure.add_subplot(projection="3d")

        for axis in [self.ax.xaxis, self.ax.yaxis, self.ax.zaxis]:
            axis.set_ticklabels([])
            axis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            axis._axinfo["grid"]['color'] = (1,1,1,0)
            
        self.ax.axis('off')

        self.canvas.draw()

        '''Render Distance'''

        self.render_val = 20

        self.render_lab = QLabel("Render Distance")
        self.render_lab.setFixedWidth(100)

        self.render_lab2 = QLabel(str(self.render_val))

        self.render_slider = QSlider(Qt.Horizontal)
        self.render_slider.setRange(0, self.render_val)
        self.render_slider.setSingleStep(1)
        self.render_slider.valueChanged.connect(self.Change_Render_Distance)
        self.render_slider.valueChanged.connect(self.render_lab2.setNum)
        self.render_slider.valueChanged.connect(self.Update_Plot)
        self.render_slider.setFixedWidth(250)
        self.render_slider.setValue(self.render_val)


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
        self.grid_layout.addWidget(self.render_lab, row, 0, 1, 1, alignment=Qt.AlignCenter)
        self.grid_layout.addWidget(self.render_slider, row, 1, 1, 1, alignment=Qt.AlignCenter)
        self.grid_layout.addWidget(self.render_lab2, row, 2, 1, 1, alignment=Qt.AlignCenter)

        row+=1
        self.grid_layout.addWidget(self.canvas, row, 0, 3, 3)
        
        

    def Add_Diacid_Chain(self):
        self.new_molecule_path = Path(self.path + "XYZ/Diacids/" + self.diacid_box.currentText().replace(" ", "_") + ".xyz")

        self.new_molecule_dict  = self.Add_File_To_Dict()
        self.new_molecule_bonds = self.Get_Bonds()

        #TODO
            # Add Molecules to chain
            # Add list of molecules already added

        self.Update_Plot()

    def Add_Diol_Chain(self):
        self

    def Add_Amino_Chain(self):
        self
    
    def Change_Angles(self):
        self.phi_val = self.phi_slider.value()
        self.theta_val = self.theta_slider.value()

    def Change_Render_Distance(self):
        self.render_val = self.render_slider.value()

    def Update_Plot(self):
        self.ax.cla()
        
        for j in range(self.new_molecule_dict['coords'].shape[0]):
            atom   = self.new_molecule_dict['atoms'][j].lower()
            coords = self.new_molecule_dict['coords'][j]
            color = self.atom_colors[atom]
            size = self.atom_size[atom]

            if np.sqrt(np.sum(coords**2)) < self.render_val:
                self.ax.scatter(*coords, color=color, s=size*500)

        for j in range(len(self.bonds)):
            x1 = self.bonds[j][0][0]
            x2 = self.bonds[j][1][0]

            y1 = self.bonds[j][0][1]
            y2 = self.bonds[j][1][1]

            z1 = self.bonds[j][0][2]
            z2 = self.bonds[j][1][2]

            x = np.asarray((x1, x2))
            y = np.asarray((y1, y2))
            z = np.asarray((z1, z2))

            p1 = np.sqrt(x1**2 + y1**2 + z1**2)
            p2 = np.sqrt(x2**2 + y2**2 + z2**2)

            if p1 < self.render_val and p2 < self.render_val:
                self.ax.plot(x, y, z, c='black')

        for axis in [self.ax.xaxis, self.ax.yaxis, self.ax.zaxis]:
            axis.set_ticklabels([])
            axis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            axis._axinfo["grid"]['color'] = (1,1,1,0)

        self.ax.axis('off')

        self.canvas.draw()


    def Add_File_To_Dict(self):
        file_dict = {}

        with open(self.new_molecule_path, 'r') as f:
            ff = f.readlines()

        num_atoms = int(ff[0])

        ff = ff[2:]

        atoms = []
        coords = np.zeros((num_atoms, 3))

        atom = 0

        while ff[-1] == '\n':
            ff = ff[:-1]

        for line in ff:
            line = re.sub(' +', ' ', line)
            line = line.split(" ")
            coord = 0
            for place in line:
                if place == '':
                    pass
                else:
                    try:
                        coords[atom, coord] = float(place)
                        coord += 1
                    except:
                        atoms.append(place)

            atom += 1

        file_dict['atoms'] = atoms
        file_dict['coords'] = coords

        return file_dict

    def Get_Bonds(self):

        self.bonds = []
        
        for j in range(self.new_molecule_dict['coords'].shape[0]):
            atom1   = self.new_molecule_dict['atoms'][j].lower()
            coords1 = self.new_molecule_dict['coords'][j]

            for i in range(j+1, self.new_molecule_dict['coords'].shape[0]):
                atom2   = self.new_molecule_dict['atoms'][i].lower()
                coords2 = self.new_molecule_dict['coords'][i]

                distance = np.sqrt(np.sum((coords1 - coords2)**2))

                if distance < (self.atom_size[atom1] + self.atom_size[atom2]) * self.bond_distance:
                    self.bonds.append([coords1, coords2])


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

