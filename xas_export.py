from PyQt5.QtWidgets import QFileDialog
from nexpy.gui.datadialogs import BaseDialog
from nexpy.gui.utils import report_error
from nexusformat.nexus.tree import *
import export_data, multi_xas

def show_dialog(parent=None):
    try:
        dialog = ExpDialog()
        dialog.show()
    except NeXusError as error:
        report_error("Export Averaged XAS Scans", error)
        

class ExpDialog(BaseDialog):

    def __init__(self, parent=None):
        
        super(ExpDialog, self).__init__(parent)
        self.select_entry()
        self.get_xas_binned()
        self.entry_box.currentIndexChanged.connect(self.get_xas_binned)
        self.set_layout(self.entry_layout, self.close_buttons())
        self.set_title('Select Binned Data Entry')
    
    def get_xas_binned(self):
        self.xas = multi_xas.XAS()
        self.xas.energy = self.entry.data.energy
        self.xas.i0 = self.entry.data.i0
        self.xas.tey = self.entry.data.tey
        self.xas.diode = self.entry.data.diode
        self.xas.pfy_sdd1 = self.entry.data.pfy_sdd1
        self.xas.pfy_sdd2 = self.entry.data.pfy_sdd2
        self.xas.pfy_sdd3 = self.entry.data.pfy_sdd3
        self.xas.pfy_sdd4 = self.entry.data.pfy_sdd4
        return self.xas
    
    def accept(self):
        try:
           filename = QFileDialog.getSaveFileName(self, "Export File", "data.xas", filter ="xas (*.xas *.)")
           export_data.export_xas(self.xas, filename)
           super(ExpDialog, self).accept()
        except NeXusError as error:
           report_error("Export Averaged XAS Scans", error)
           super(ExpDialog, self).reject()
