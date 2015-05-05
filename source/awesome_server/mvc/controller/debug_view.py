from awesome_server.mvc.controller.extended_controller import ExtendedController
from awesome_server.mvc.models.connection_manager import ConnectionManagerModel

import gtk
from twisted.internet import reactor

from awesome_server.utils.config import global_server_config


class DebugViewController(ExtendedController):

    def __init__(self, model, view):
        assert isinstance(model, ConnectionManagerModel)
        ExtendedController.__init__(self, model, view)

        model.connection_manager.add_tcp_connection(global_server_config.get_config_value("TCP_PORT"))
        model.connection_manager.add_udp_connection(global_server_config.get_config_value("UDP_PORT"))

        view["send_button"].connect("clicked", self.send_button_clicked)
        view["send_ack_button"].connect("clicked", self.send_ack_button_clicked)
        # view["send_exe_button"].connect("clicked", self.send_exe_button_clicked)

    def send_button_clicked(self, widget, event=None):
        self.send_message_to_selected_connection(self.view["entry"].get_text(), False, False)

    def send_ack_button_clicked(self, widget, event=None):
        self.send_message_to_selected_connection(self.view["entry"].get_text(), exe=False)

    def on_start_button_clicked(self, widget, event=None):
        self.send_message_to_selected_connection("RUN")

    def on_pause_button_clicked(self, widget, event=None):
        self.send_message_to_selected_connection("PAUSE")

    def on_stop_button_clicked(self, widget, event=None):
        self.send_message_to_selected_connection("STOP")

    def on_stepm_button_clicked(self, widget, event=None):
        self.send_message_to_selected_connection("STEPM")

    def on_stepf_button_clicked(self, widget, event=None):
        self.send_message_to_selected_connection("STEPF")

    def on_stepb_button_clicked(self, widget, event=None):
        self.send_message_to_selected_connection("STEPB")

    def on_window_destroy(self, widget, event=None):
        reactor.stop()
        gtk.main_quit()

    def send_message_to_selected_connection(self, message, ack=True, exe=True):
        combo = self.view["combobox"]
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            name, ip, port = model[tree_iter]

            con = self.model.get_udp_connection_for_address((ip, port))
            if con:
                if ack and exe:
                    con.send_acknowledged_message(message, (ip, port), "EXE")
                elif ack:
                    con.send_acknowledged_message(message, (ip, port))
                else:
                    con.send_non_acknowledged_message(message, (ip, port))

    @ExtendedController.observe("_udp_clients", after=True)
    def add_udp_client(self, model, prop_name, info):
        clients = info.instance[info.args[0]]
        if self.view:
            last_index = len(clients) - 1
            ip, port = clients[last_index]
            self.view["liststore"].append(["%s:%d" % (ip, port), ip, port])
            self.view["combobox"].set_active(last_index)

    @ExtendedController.observe("_tcp_messages_received", after=True)
    def handle_tcp_message_received(self, model, prop_name, info):
        self.print_msg(str(info["args"]))

    @ExtendedController.observe("_udp_messages_received", after=True)
    def handle_udp_message_received(self, mode, prop_name, info):
        message = info["args"][1]
        self.print_msg(message)

    def print_msg(self, msg):
        buf = self.view["messages"].get_buffer()
        buf.insert(buf.get_end_iter(), msg + "\n")
        self.view["messages"].scroll_mark_onscreen(buf.get_insert())