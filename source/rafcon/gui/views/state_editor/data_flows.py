# Copyright (C) 2014-2017 DLR
#
# All rights reserved. This program and the accompanying materials are made
# available under the terms of the Eclipse Public License v1.0 which
# accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
# Franz Steinmetz <franz.steinmetz@dlr.de>
# Lukas Becker <lukas.becker@dlr.de>
# Matthias Buettner <matthias.buettner@dlr.de>
# Rico Belder <rico.belder@dlr.de>
# Sebastian Brunner <sebastian.brunner@dlr.de>

from gtkmvc3.view import View

from rafcon.gui import glade
from rafcon.gui.views.utils.tree import TreeView
import rafcon.gui.helpers.label as gui_helper_label
from rafcon.gui.utils import constants


class StateDataFlowsListView(TreeView):
    builder = glade.get_glade_path("data_flow_list_widget.glade")
    top = 'tree_view'

    def __init__(self):
        super(StateDataFlowsListView, self).__init__()
        self.tree_view = self['tree_view']


class StateDataFlowsEditorView(View):
    builder = glade.get_glade_path("state_data_flows_widget.glade")
    top = 'data_flows_container'

    def __init__(self):
        View.__init__(self)

        self.data_flows_listView = StateDataFlowsListView()
        self['data_flows_scroller'].add(self.data_flows_listView.get_top_widget())
        self.data_flows_listView.scrollbar_widget = self['data_flows_scroller']

        self['internal_d_checkbutton'].set_border_width(constants.BUTTON_BORDER_WIDTH)
        self['connected_to_d_checkbutton'].set_border_width(constants.BUTTON_BORDER_WIDTH)
        self['add_d_button'].set_border_width(constants.BUTTON_BORDER_WIDTH)
        self['remove_d_button'].set_border_width(constants.BUTTON_BORDER_WIDTH)

        gui_helper_label.ellipsize_labels_recursively(self['data_flows_toolbar'])
