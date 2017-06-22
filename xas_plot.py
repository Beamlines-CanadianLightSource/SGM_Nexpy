import numpy as np
from nexpy.gui.datadialogs import BaseDialog, GridParameters
from nexpy.gui.utils import report_error
from nexusformat.nexus import nxload, NeXusError, NXentry, NXdata, NXroot, NXfield
from nexusformat.nexus.tree import * 

def show_dialog(parent=None):
    try:
        dialog = XasDialog()
        dialog.show()
    except NeXusError as error:
        report_error("Plot single XAS Scans", error)
        

class XasDialog(BaseDialog):

    def __init__(self, parent=None):
        
        super(XasDialog, self).__init__(parent)
        self.select_entry()
        dets_list = {}
        self.dets = self.entry['instrument/absorbed_beam']
        self.signal_combo = self.select_box(self.dets, default='sdd3_2', slot=self.plot_xas)
        self.lab_sig = self.labels('Signal :', align='left')
        self.set_layout(self.entry_layout, self.lab_sig, self.signal_combo, self.close_buttons())
        self.set_title('Plot Single XAS')
        self.plot_xas()
    
    @property
    def signal_s(self):
        return np.array(self.entry.instrument.absorbed_beam[self.signal_combo.currentText()])

    @property
    def energy(self):
        return np.array(self.entry.instrument.monochromator.en)

    def plot_xas(self):
        self.singleXas = NXdata(self.signal_s, self.energy)
        self.singleXas.plot(xmin = min(self.energy), xmax=max(self.energy), ymin = min(self.signal_s), ymax = max(self.signal_s))
        return

    def accept(self):
        try:
           self.plot_xas
           super(XasDialog, self).accept()
        except NeXusError as error:
           report_error("Plot Single XAS", error)
           super(XasDialog, self).reject()
