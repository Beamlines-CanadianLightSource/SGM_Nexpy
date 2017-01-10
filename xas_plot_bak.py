import numpy as np
from nexpy.gui.datadialogs import BaseDialog, GridParameters
from nexpy.gui.utils import report_error
from nexusformat.nexus import nxload, NeXusError, NXentry, NXdata, NXroot
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
        self.signal_combo = self.select_box(self.dets, default='sdd3_2', slot=plot_xas) 
        self.energy = self.entry['instrument/monochromator/en']
        
        self.lab_sig = self.labels('Signal :', align='left')
        self.set_layout(self.entry_layout, self.lab_sig, self.signal_combo, self.close_buttons())
        self.set_title('Plot Single XAS')

    @property
    def signal(self):
        return self.signal_combo.currentText()

    def plot_xas(self):
        self.x1 = np.array(self.energy)
        self.y1 = np.array(self.entry['instrument/absorbed_beam'][self.signal])
        try:
            self.tree.singleXas = NXroot(NXentry(NXdata(yi, xi)))
        except:
            self.tree.singleXas['entry/data'][self.signal] = NXfield(yi)
        
        self.tree.singleXas.oplot(xmin = min(self.x1), xmax=max(self.x1), ymin = min(self.y1), ymax = max(self.y1))
        return x1, y1

    def accept(self):
        try:
            self.plot_map()
            super(XasDialog, self).accept()
        except NeXusError as error:
            report_error("Plot Single XAS", error)
            super(XasDialog, self).reject()
