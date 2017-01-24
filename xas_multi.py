import numpy as np
from nexpy.gui.pyqt import QtGui
from PyQt4.QtCore import *
from nexpy.gui.datadialogs import BaseDialog, GridParameters
from nexpy.gui.utils import report_error
# from nexusformat.nexus import nxload, NeXusError, NXentry, NXdata, NXroot, NXfield
from nexusformat.nexus.tree import * 
from . import multi_xas, export_data
from customize_gui import QHLine

def show_dialog(parent=None):
    try:
        dialog = MultiXasDialog()
        dialog.show()
    except NeXusError as error:
        report_error("Plot multi XAS Scans", error)
        

class MultiXasDialog(BaseDialog):

    def __init__(self, parent=None):
        
        super(MultiXasDialog, self).__init__(parent)
        layout = QtGui.QVBoxLayout()

        self.h_line = QHLine()
        self.h_line2 = QHLine()
        self.h_line3 = QHLine()
       
        self.select_root(text='Select File :')
        self.select_entry_num(text='First Entry :')
        self.select_entry_num(text='Last Entry :', other='True')
        self.select_abs()
        self.select_sdd()

        self.roi_peak_slider()
        self.roi_width_slider()
        
        self.pb_ploteems = QtGui.QPushButton()
        self.pb_ploteems.setObjectName("plot eems")
        self.pb_ploteems.setText("Plot EEMS")

        self.pb_getsumplot = QtGui.QPushButton()
        self.pb_getsumplot.setObjectName("summary plot")
        self.pb_getsumplot.setText("Summary Plot")

        self.pb_get_averaged = QtGui.QPushButton()
        self.pb_get_averaged.setObjectName("interpolated plots")
        self.pb_get_averaged.setText("Interpolated Plots")

        self.pb_get_single_averaged = QtGui.QPushButton()
        self.pb_get_single_averaged.setObjectName("single interpolated plot")
        self.pb_get_single_averaged.setText("Single Interpolated Plot")

        self.pb_get_normalized = QtGui.QPushButton()
        self.pb_get_normalized.setObjectName("normalized data")
        self.pb_get_normalized.setText("Normalized Data")

        self.bad_scans = QtGui.QLineEdit()
        self.bad_scans.setObjectName("Bad Scans")

        layout.addLayout(self.root_layout)
        layout.addLayout(self.select_sdd())
        layout.addWidget(self.pb_ploteems)
        layout.addWidget(self.h_line)

        layout.addLayout(self.entry_num_layout)
        layout.addLayout(self.other_entry_num_layout)

        layout.addLayout(self.roi_peak_slider())
        layout.addLayout(self.roi_width_slider())

        layout.addLayout(self.select_abs())
        layout.addWidget(self.pb_getsumplot)
        layout.addWidget(self.h_line2)

        bad_scan_layout = QtGui.QHBoxLayout()
        bad_scan_layout.addWidget(QtGui.QLabel('Bad Scans : '))
        bad_scan_layout.addWidget(self.bad_scans)
        layout.addLayout(bad_scan_layout)
        layout.addWidget(self.pb_get_averaged)
        layout.addWidget(self.h_line3)

        layout.addLayout(self.select_normalization())
        layout.addWidget(self.pb_get_normalized)

        # layout.addWidget(self.close_buttons())
        
        self.setLayout(layout)
        self.pb_ploteems.clicked.connect(self.plot_eems)
        self.pb_getsumplot.clicked.connect(self.plot_sum)
        self.pb_get_averaged.clicked.connect(self.plot_averaged_data)
        self.pb_get_normalized.clicked.connect(self.plot_normalized_data)
        self.root_box.currentIndexChanged.connect(self.refresh_entry)
        self.set_title('Multi XAS')
   
    @property
    def start(self):
        return int(self.entry_num_box.currentText()) 

    @property
    def end(self):
        return int(self.other_entry_num_box.currentText()) 

    @property
    def bad_scan_list(self):
        return self.bad_scans.text()

    @property
    def sdd(self):
        return self.select_sdd_box.currentText()

    def refresh_entry(self):
        self.entry_num_box.clear()
        self.other_entry_num_box.clear()
        entries = []
        for entry in range(len(self.root.NXentry)):
            entries.append(entry)
        for entry in sorted(entries):
            self.entry_num_box.addItem(str(entry + 1))
            self.other_entry_num_box.addItem(str(entry + 1))

        return

    def select_entry_num(self, text= 'Select Entry :', other=False):
        layout = QtGui.QHBoxLayout()
        box = QtGui.QComboBox()
        box.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        entries = []
        for entry in range(len(self.root.NXentry)):
            entries.append(entry)
        for entry in sorted(entries):
            box.addItem(str(entry + 1))
        
        layout.addWidget(QtGui.QLabel(text))
        layout.addWidget(box)
        layout.addStretch()
        if not other:
            self.entry_num_box = box
            self.entry_num_layout = layout
        else:
            self.other_entry_num_box = box
            self.other_entry_num_layout = layout

        return layout    

    @property
    def sum_det(self):
        return self.select_abs_box.currentText()

    # drop down menu to select detector for summary plot
    def select_abs(self, text='Select Detector :'):
        layout = QtGui.QHBoxLayout()
        box = QtGui.QComboBox()
        box.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        sdds = ['TEY', 'I0', 'DIODE','PFY_SDD1', 'PFY_SDD2','PFY_SDD3','PFY_SDD4']
        for sdd in sorted(sdds):
            box.addItem(sdd)

        box.setCurrentIndex(2)
        self.select_abs_box = box
        self.select_abs_layout = layout

        layout.addWidget(QtGui.QLabel(text))
        layout.addWidget(box)
        layout.addStretch()
        return layout

    # drop down menu to select sdd
    def select_sdd(self, text='Select SDD :'):
        layout = QtGui.QHBoxLayout()
        box = QtGui.QComboBox()
        box.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        sdds = ['SDD1', 'SDD2', 'SDD3','SDD4']
        for sdd in sorted(sdds):
            box.addItem(sdd)
        
        self.select_sdd_box = box
        self.select_sdd_layout = layout

        layout.addWidget(QtGui.QLabel(text))
        layout.addWidget(box)
        layout.addStretch()
        return layout

    @property
    def normalization_dividend(self):
        return self.select_dividend_box.currentText()

    @property
    def normalization_divisor(self):
        return self.select_divisor_box.currentText()

    # drop down menu to select dividend and divisor
    def select_normalization(self, text = 'Normalization: '):

        layout = QtGui.QHBoxLayout()
        # dividend
        box = QtGui.QComboBox()
        box.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        sdds = ['PFY_SDD1', 'PFY_SDD2','PFY_SDD3','PFY_SDD4']
        for sdd in sorted(sdds):
            box.addItem(sdd)

        self.select_dividend_box = box
        # self.select_abs_layout = layout

        # divisor
        box2 = QtGui.QComboBox()
        box2.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        sdds2 = ['I0', 'TEY', 'DIODE']
        for sdd2 in sorted(sdds2):
            box2.addItem(sdd2)

        box2.setCurrentIndex(1)
        self.select_divisor_box = box2

        layout.addWidget(QtGui.QLabel(text))
        layout.addWidget(box)
        layout.addWidget(box2)
        layout.addStretch()
        return layout

    @property
    def peak(self):
        return self.roi_peak.value()

    @property
    def width(self):
        return self.roi_width.value()

    @property
    def roi_up(self):
        up = self.peak + self.width/2
        if up > 256:
            return 256

        return up

    @property
    def roi_dn(self):
        dn = self.peak - self.width/2
        if dn < 0:
            return 0

        return dn

    def roi_peak_slider(self, text='ROI Peak :'):
        roi_peak_layout = QtGui.QHBoxLayout()
        roi_peak_layout.addWidget(QtGui.QLabel(text))
        self.roi_peak = QtGui.QSlider(Qt.Horizontal)
        self.pLabel = QtGui.QLabel('800 eV')
        self.roi_peak.setMinimum(0)
        self.roi_peak.setMaximum(256)
        self.roi_peak.setValue(80)
        self.roi_peak.setTickPosition(QtGui.QSlider.TicksBelow)
        self.roi_peak.setTickInterval(1)
        roi_peak_layout.addWidget(self.roi_peak)
        self.roi_peak.valueChanged.connect(self.setRoi)
        roi_peak_layout.addWidget(self.pLabel)
        return roi_peak_layout

    def roi_width_slider(self, text='ROI Width :'):
        roi_width_layout = QtGui.QHBoxLayout()
        roi_width_layout.addWidget(QtGui.QLabel(text))
        self.roi_width = QtGui.QSlider(Qt.Horizontal)
        self.wLabel = QtGui.QLabel('200 eV')
        self.roi_width.setMinimum(2)
        self.roi_width.setMaximum(100)
        self.roi_width.setValue(20)
        self.roi_width.setTickPosition(QtGui.QSlider.TicksBelow)
        self.roi_peak.setTickInterval(1)
        roi_width_layout.addWidget(self.roi_width)
        self.roi_width.valueChanged.connect(self.setRoi)
        roi_width_layout.addWidget(self.wLabel)
        return roi_width_layout
   
    def setRoi(self):
        self.roi_width_label()
        self.roi_peak_label()
        return self.roi_dn, self.roi_up 
  
    def roi_peak_label(self):
        self.pLabel.setText(str(self.peak) + '0' + ' eV')
        return self.pLabel

    def roi_width_label(self):
        self.wLabel.setText(str(self.width) + '0' + ' eV')
        return self.wLabel
 
    def plot_sum(self):
        self.xas = multi_xas.getMultiXAS(self.root, range_start = self.start, range_end = self.end)
        self.xas.getpfy(self.roi_dn, self.roi_up)
        self.xas.summary_plot(self.sum_det)
        # return

    def plot_eems(self):
        self.xas = multi_xas.getMultiXAS(self.root, range_start = self.start, range_end = self.end)
        multi_xas.eem(self.xas, self.sdd)
        return self.xas

    def plot_averaged_data(self):
        self.avg_xas()

    # def plot_single_averaged_data(self):
    #     multi_xas.plot_avg_xas_single(self.bin_xas, self.binned_det)

    @property
    def start_en(self):
        energy = np.array(self.root.NXentry[self.start]['instrument/monochromator/en'])
        return np.amin(energy)
    
    @property
    def end_en(self):
        energy = np.array(self.root.NXentry[self.start]['instrument/monochromator/en'])
        return np.amax(energy)

    def avg_xas(self):
        self.xas = multi_xas.getMultiXAS(self.root, range_start = self.start, range_end = self.end)
        self.xas.getpfy(self.roi_dn, self.roi_up)
        print self.bad_scan_list
        good_xas = multi_xas.get_good_scan(self.xas, ban_scan_list = [self.bad_scan_list])
        self.bin_xas = multi_xas.binned_xas(good_xas, start_energy = self.start_en, end_energy = self.end_en, bin_interval = 0.1)
        multi_xas.plot_avg_xas_all(self.bin_xas)
        scan_entry = str(self.root) + '_' + 'scans' + '_' + str(self.start) + '_' + str(self.end)
        try:
            self.tree.binned_data = NXroot()
            self.tree.binned_data[scan_entry] = NXentry(NXdata())
            self.tree.binned_data[scan_entry].data.energy = NXfield(self.bin_xas.energy)
            self.tree.binned_data[scan_entry].data.tey = NXfield(self.bin_xas.tey)
            self.tree.binned_data[scan_entry].data.i0 = NXfield(self.bin_xas.i0)
            self.tree.binned_data[scan_entry].data.diode = NXfield(self.bin_xas.diode)
            self.tree.binned_data[scan_entry].data.pfy_sdd1 = NXfield(self.bin_xas.pfy_sdd1)
            self.tree.binned_data[scan_entry].data.pfy_sdd2 = NXfield(self.bin_xas.pfy_sdd2)
            self.tree.binned_data[scan_entry].data.pfy_sdd3 = NXfield(self.bin_xas.pfy_sdd3)
            self.tree.binned_data[scan_entry].data.pfy_sdd4 = NXfield(self.bin_xas.pfy_sdd4)
        except:
            try:
                self.tree.binned_data[scan_entry] = NXentry(NXdata())
                self.tree.binned_data[scan_entry].data.energy = NXfield(self.bin_xas.energy)
                self.tree.binned_data[scan_entry].data.tey = NXfield(self.bin_xas.tey)
                self.tree.binned_data[scan_entry].data.i0 = NXfield(self.bin_xas.i0)
                self.tree.binned_data[scan_entry].data.diode = NXfield(self.bin_xas.diode)
                self.tree.binned_data[scan_entry].data.pfy_sdd1 = NXfield(self.bin_xas.pfy_sdd1)
                self.tree.binned_data[scan_entry].data.pfy_sdd2 = NXfield(self.bin_xas.pfy_sdd2)
                self.tree.binned_data[scan_entry].data.pfy_sdd3 = NXfield(self.bin_xas.pfy_sdd3)
                self.tree.binned_data[scan_entry].data.pfy_sdd4 = NXfield(self.bin_xas.pfy_sdd4)
            except:
                del self.tree.binned_data[scan_entry]
                self.tree.binned_data[scan_entry] = NXentry(NXdata())
                self.tree.binned_data[scan_entry].data.energy = NXfield(self.bin_xas.energy)
                self.tree.binned_data[scan_entry].data.tey = NXfield(self.bin_xas.tey)
                self.tree.binned_data[scan_entry].data.i0 = NXfield(self.bin_xas.i0)
                self.tree.binned_data[scan_entry].data.diode = NXfield(self.bin_xas.diode)
                self.tree.binned_data[scan_entry].data.pfy_sdd1 = NXfield(self.bin_xas.pfy_sdd1)
                self.tree.binned_data[scan_entry].data.pfy_sdd2 = NXfield(self.bin_xas.pfy_sdd2)
                self.tree.binned_data[scan_entry].data.pfy_sdd3 = NXfield(self.bin_xas.pfy_sdd3)
                self.tree.binned_data[scan_entry].data.pfy_sdd4 = NXfield(self.bin_xas.pfy_sdd4)

        self.tree.binned_data[scan_entry].data.signal = NXattr(self.sum_det.lower())
        self.tree.binned_data[scan_entry].data.axes = NXattr("energy")
        return 

    def plot_normalized_data(self):
        energy, normalized_array = multi_xas.plot_normalized(self.bin_xas, dividend = self.normalization_dividend, divisor = self.normalization_divisor)
        try:
            scan_entry = "normalized"
            self.tree.normalized_data = NXroot()
            self.tree.normalized_data[scan_entry] = NXentry(NXdata())
            self.tree.normalized_data[scan_entry].data.energy = NXfield(energy)
            self.tree.normalized_data[scan_entry].data.normalized = NXfield(normalized_array)
        except:
            print ("Error occurred when exported normalized data into the file")

    # def accept(self):
    #     try:
    #        self.avg_xas()
    #        super(MultiXasDialog, self).accept()
    #     except NeXusError as error:
    #        report_error("Multi XAS", error)
    #        super(MultiXasDialog, self).reject()
