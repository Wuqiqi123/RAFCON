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

from gtkmvc import View

import rafcon.gui.helpers.label as gui_helper_label
from rafcon.gui.utils import constants


class StateDataFlowsListView(View):
    builder = constants.get_glade_path("data_flow_list_widget.glade")
    top = 'tree_view'

    def __init__(self):
        View.__init__(self)
        self.tree_view = self['tree_view']

    def get_top_widget(self):
        return self.tree_view


class StateDataFlowsEditorView(View):
    builder = constants.get_glade_path("state_data_flows_widget.glade")
    top = 'data_flows_container'

    def __init__(self):
        View.__init__(self)

        gui_helper_label.set_label_markup(self['data_flows_label'], 'DATA FLOWS',
                                          letter_spacing=constants.LETTER_SPACING_1PT)

        self.data_flows_listView = StateDataFlowsListView()
        self['dataflows_scroller'].add(self.data_flows_listView.get_top_widget())

        self['internal_d_checkbutton'].set_border_width(constants.BUTTON_BORDER_WIDTH)
        self['connected_to_d_checkbutton'].set_border_width(constants.BUTTON_BORDER_WIDTH)
        self['add_d_button'].set_border_width(constants.BUTTON_BORDER_WIDTH)
        self['remove_d_button'].set_border_width(constants.BUTTON_BORDER_WIDTH)