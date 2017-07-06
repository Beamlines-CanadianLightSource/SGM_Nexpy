import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QSizePolicy, QSlider, QLabel
from nexpy.gui.datadialogs import BaseDialog
from nexpy.gui.utils import report_error
from nexusformat.nexus.tree import *
from matplotlib.mlab import griddata
import matplotlib.pyplot as plt
from numpy import linspace, meshgrid


def show_dialog(parent=None):
    try:
        dialog = MapDialog()
        dialog.show()
    except NeXusError as error:
        report_error("Making 2D map from data", error)


class MapDialog(BaseDialog):
    def __init__(self, parent=None):

        super(MapDialog, self).__init__(parent)

        self.select_entry()
        dets_list = {}
        self.dets = self.entry['instrument/fluorescence']
        self.axes = self.entry['sample/positioner']
        self.signal_combo = self.select_box(self.dets, default='sdd3')
        self.axis1_combo = self.select_box(self.axes, default='hex_xp')
        self.axis2_combo = self.select_box(self.axes, default='hex_yp')



        roi_peak_layout = QHBoxLayout()
        roi_peak_layout.addWidget(QLabel('ROI Peak'))
        self.roi_peak = QSlider(Qt.Horizontal)
        self.pLabel = QLineEdit()
        self.pLabel.setText('800')
        self.pLabel.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.pLabel.setAlignment(Qt.AlignRight)
        self.roi_peak.setMinimum(0)
        self.roi_peak.setMaximum(256)
        self.roi_peak.setValue(80)
        self.roi_peak.setTickPosition(QSlider.TicksBelow)
        self.roi_peak.setTickInterval(1)
        roi_peak_layout.addWidget(self.roi_peak)
        self.roi_peak.valueChanged.connect(self.setRoi)
        self.pLabel.returnPressed.connect(self.setRoi2)
        self.pUnits = QLabel('eV')
        roi_peak_layout.addWidget(self.pLabel)
        roi_peak_layout.addWidget(self.pUnits)

        roi_width_layout = QHBoxLayout()
        roi_width_layout.addWidget(QLabel('ROI Width'))
        self.roi_width = QSlider(Qt.Horizontal)
        self.wLabel = QLineEdit()
        self.wLabel.setText('200')
        self.wLabel.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
        self.wLabel.setAlignment(Qt.AlignRight)
        self.roi_width.setMinimum(2)
        self.roi_width.setMaximum(100)
        self.roi_width.setValue(20)
        self.roi_width.setTickPosition(QSlider.TicksBelow)
        self.roi_peak.setTickInterval(1)
        roi_width_layout.addWidget(self.roi_width)

        self.roi_width.valueChanged.connect(self.setRoi)
        self.wLabel.returnPressed.connect(self.setRoi2)
        self.signal_combo.activated.connect(self.setRoi)
        self.axis1_combo.activated.connect(self.setRoi)
        self.axis2_combo.activated.connect(self.setRoi)
        self.entry_box.activated.connect(self.setRoi)

        self.wUnits = QLabel('eV')
        roi_width_layout.addWidget(self.wLabel)
        roi_width_layout.addWidget(self.wUnits)

        lab_sig_layout = QHBoxLayout()
        self.lab_sig = self.labels('Detector :', align='left')
        lab_sig_layout.addLayout(self.lab_sig)
        lab_sig_layout.addWidget(self.signal_combo)
        lab_sig_layout.addStretch()

        lab_axis1_layout = QHBoxLayout()
        self.lab_axis1 = self.labels('X-Axis :', align='left')
        lab_axis1_layout.addLayout(self.lab_axis1)
        lab_axis1_layout.addWidget(self.axis1_combo)
        lab_axis1_layout.addStretch()

        lab_axis2_layout = QHBoxLayout()
        self.lab_axis2 = self.labels('Y-Axis :', align='left')
        lab_axis2_layout.addLayout(self.lab_axis2)
        lab_axis2_layout.addWidget(self.axis2_combo)
        lab_axis2_layout.addStretch()

        self.contours = QLineEdit("100")
        self.contours.setObjectName("Number of Contours")
        contour_layout = QHBoxLayout()
        contour_layout.addWidget(QLabel('# of Contours : '))
        contour_layout.addWidget(self.contours)

        self.set_layout(self.entry_layout, lab_sig_layout, lab_axis1_layout,
                        lab_axis2_layout, roi_peak_layout, roi_width_layout, contour_layout, self.close_buttons())
        self.set_title('Convert to 2D map')
        self.setRoi()

    @property
    def signal(self):
        return self.signal_combo.currentText()

    @property
    def axis1(self):
        return self.axis1_combo.currentText()

    @property
    def axis2(self):
        return self.axis2_combo.currentText()

    @property
    def depth(self):
        try:
            value = int(self.contours.text())
            return value
        except:
            return 1000

    def get_pLabel(self):
        value = int(self.pLabel.text())
        value = value / 10
        return value

    def get_wLabel(self):
        value = int(self.wLabel.text())
        value = value / 10
        return value

    @property
    def roi_up(self):
        up = self.peak + self.width / 2
        if up > 256:
            return 256
        return int(up)

    @property
    def roi_dn(self):
        dn = self.peak - self.width / 2
        if dn < 0:
            return 0
        return int(dn)

    def roi_peak_label(self):
        self.roi_peak.setValue(self.peak)
        self.pLabel.setText(str(self.peak) + '0')
        return self.pLabel

    def roi_width_label(self):
        self.roi_width.setValue(self.width)
        self.wLabel.setText(str(self.width) + '0')
        return self.wLabel

    def setRoi2(self):
        self.roi_width.setValue(self.get_wLabel())
        self.roi_peak.setValue(self.get_pLabel())
        return

    def setRoi(self):
        self.peak = self.roi_peak.value()
        self.width = self.roi_width.value()
        self.roi_width_label()
        self.roi_peak_label()
        self.plot_map()
        return int(self.roi_dn), int(self.roi_up)

    def getylen(self):
        command = self.entry['command']
        if str(command).split(" ")[0] == "cmesh":
            str_n = str(command).split(" ")[8]
            num = int(str_n)
            return num
        else:
            return False

    def grid(self, x, y, z, resX, resY):
        shift = 0.5
        x_ad = x
        xi = linspace(min(x), max(x), resX)
        yi = linspace(min(y), max(y), resY)
        for i in range(1, len(x)):
            x_ad[i] = x[i] + shift * (x[i] - x[i - 1])

        Z = griddata(x_ad, y, z, xi, yi, interp='linear')
        X, Y = meshgrid(xi, yi)
        return X, Y, Z, xi, yi

    def plot_map(self):
        self.x1 = np.array(self.entry['sample/positioner'][self.axis1])
        self.y1 = np.array(self.entry['sample/positioner'][self.axis2])
        self.sdd = np.array(self.entry['instrument/fluorescence'][self.signal])
        row, col = np.shape(self.sdd)
        self.z1 = np.zeros(row)
        for i in range(0, row):
            self.z1[i] = self.sdd[i, self.roi_dn:self.roi_up].sum(axis=0)

        self.ylen = self.getylen()
        if self.ylen:
            self.xlen = len(self.entry['sample/positioner'][self.axis1]) / self.ylen
        else:
            self.ylen = 100
            self.xlen = 100

        X, Y, Z, xi, yi = self.grid(self.x1, self.y1, self.z1, self.xlen, self.ylen)
        self.data = NXdata(Z, [yi, xi])
        self.data.plot(xmin=min(self.x1), xmax=max(self.x1), ymin=min(self.y1), ymax=max(self.y1), zmin=min(self.z1),
                       zmax=max(self.z1))
        return X, Y, Z, xi, yi

    def save_map(self):
        X, Y, Z, xi, yi = self.plot_map()
        try:
            self.tree.map2ddata = NXroot()
            self.tree.map2ddata['roi' + '_' + str(self.roi_dn) + ':' + str(self.roi_up)] = NXentry()
            self.tree.map2ddata['roi' + '_' + str(self.roi_dn) + ':' + str(self.roi_up)]['data'] = NXdata(Z, [yi, xi])

        except:
            try:
                self.tree.map2ddata['roi' + '_' + str(self.roi_dn) + ':' + str(self.roi_up)] = NXentry()
                self.tree.map2ddata['roi' + '_' + str(self.roi_dn) + ':' + str(self.roi_up)]['data'] = NXdata(Z,
                                                                                                              [yi, xi])
            except:
                del self.tree.map2ddata['roi' + '_' + str(self.roi_dn) + ':' + str(self.roi_up)]
                self.tree.map2ddata['roi' + '_' + str(self.roi_dn) + ':' + str(self.roi_up)] = NXentry()
                self.tree.map2ddata['roi' + '_' + str(self.roi_dn) + ':' + str(self.roi_up)]['data'] = NXdata(Z,
                                                                                                              [yi, xi])
        minim = np.amin(Z)
        maxim = np.amax(Z)
        levels = linspace(minim, maxim, self.depth)
        print(levels)
        plt.figure()
        plt.contourf(X, Y, Z, levels)
        plt.gca().invert_yaxis()
        plt.gca().invert_xaxis()
        plt.xlabel('x (mm)')
        plt.ylabel('y (mm)')
        plt.title("2D Contour Map")
        plt.colorbar()
        plt.show()
        return self.tree.map2ddata

    def accept(self):
        try:
            self.save_map()
            super(MapDialog, self).accept()
        except NeXusError as error:
            report_error("Converting 2D map", error)
            super(MapDialog, self).reject()
