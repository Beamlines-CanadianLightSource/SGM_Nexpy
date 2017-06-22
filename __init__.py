from __future__ import absolute_import
from . import map_plot, xas_plot, xas_export, xas_multi

def plugin_menu():
    menu = 'SGMPy'
    actions = []
    actions.append(('Plot Detector vs Energy', xas_plot.show_dialog))
    actions.append(('Plot 2D Map', map_plot.show_dialog))
    actions.append(('Multi XAS Processing', xas_multi.show_dialog))
    actions.append(('Export Multi XAS', xas_export.show_dialog))
    return menu, actions
