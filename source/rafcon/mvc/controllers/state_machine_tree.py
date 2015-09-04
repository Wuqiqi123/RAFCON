import gtk
import gobject

from rafcon.mvc.controllers.extended_controller import ExtendedController
from rafcon.mvc.models import ContainerStateModel
from rafcon.mvc.models.state_machine_manager import StateMachineManagerModel
from rafcon.mvc.history import parent_state_of_notification_source
from rafcon.utils import log
logger = log.get_logger(__name__)

# TODO Comment


class StateMachineTreeController(ExtendedController):

    def __init__(self, model, view):
        """Constructor
        :param model StateMachineModel should be exchangeable
        """
        assert isinstance(model, StateMachineManagerModel)

        ExtendedController.__init__(self, model, view)

        self.view_is_registered = False
        self.tree_store = gtk.TreeStore(str, str, str, gobject.TYPE_PYOBJECT, str)
        view.set_model(self.tree_store)
        #view.set_hover_expand(True)
        self.state_row_iter_dict_by_state_path = {}
        self.__my_selected_sm_id = None
        self._selected_sm_model = None

        self.no_cursor_selection = False

        self.__buffered_root_state = None  # needed to handle exchange of root_state
        self.__expansion_state = {}

        self.register()

    def register_view(self, view):
        self.view.connect('cursor-changed', self.on_cursor_changed)
        self.view_is_registered = True
        self.update(with_expand=True)

    def register_adapters(self):
        pass

    def register(self):

        """
        Change the state machine that is observed for new selected states to the selected state machine.
        :return:
        """
        # print "state_machine_tree register state_machine"
        # relieve old models
        if self.__my_selected_sm_id is not None:  # no old models available
            self.relieve_model(self.__buffered_root_state)
            self.relieve_model(self._selected_sm_model)
        # set own selected state machine id
        self.__my_selected_sm_id = self.model.selected_state_machine_id
        if self.__my_selected_sm_id is not None:
            # observe new models
            self._selected_sm_model = self.model.state_machines[self.__my_selected_sm_id]
            # logger.debug("NEW SM SELECTION %s" % self._selected_sm_model)
            self.__buffered_root_state = self._selected_sm_model.root_state
            self.observe_model(self._selected_sm_model.root_state)
            self.observe_model(self._selected_sm_model)  # for selection
            self.update()
        else:
            self.tree_store.clear()

    @ExtendedController.observe("state", after=True)  # root_state
    @ExtendedController.observe("states", after=True)
    def states_update(self, model, property, info):
        # print info
        overview = parent_state_of_notification_source(model, info.prop_name, info, "after", False)

        if overview['prop_name'][-1] == 'state' and \
                overview['method_name'][-1] in ["name"]:  # , "add_state", "remove_state"]:
            # print "do update", model.state.name
            # self.update(model)
            self.update_tree_store_row(overview['model'][-1])
        elif overview['prop_name'][-1] == 'state' and \
                overview['method_name'][-1] in ["add_state", "remove_state"]:
            # print "do update", model.state.name, overview['method_name'][-1]
            self.update(model)
            # self.update_tree_store_row(overview['model'][-1])
        else:
            if overview['prop_name'][-1] == 'state' and \
                    overview['method_name'][-1] in ["add_input_data_port", "remove_input_data_port",
                                                    "add_output_data_port", "remove_output_data_port",
                                                    "add_scoped_variable", "remove_scoped_variable",
                                                    "add_outcome", "remove_outcome",
                                                    "add_data_flow", "remove_data_flow",
                                                    "add_transition", "remove_transition"]:
                return
            self.store_expansion_state()
            self.update()  # TODO finally the state-machine tree has to be stable without this
            self.redo_expansion_state()

    @ExtendedController.observe("root_state", assign=True)
    def state_machine_notification(self, model, property, info):
        if self.__my_selected_sm_id is not None:  # no old models available
            self.relieve_model(self.__buffered_root_state)
            # self.observe_model(info.new)
            # self.__buffered_root_state = info.new
            self.observe_model(self._selected_sm_model.root_state)
            self.__buffered_root_state = self._selected_sm_model.root_state
        self.update(model.root_state)

    @ExtendedController.observe("selected_state_machine_id", assign=True)
    def state_machine_manager_notification(self, model, property, info):
        # store expansion state
        self.store_expansion_state()
        # register new state machine
        self.register()
        self.assign_notification_selection(None, None, None)
        # redo expansion state
        self.redo_expansion_state()

    def store_expansion_state(self):
        # print "\n\n store of state machine {0} \n\n".format(self.__my_selected_sm_id)
        try:
            act_expansion_state = {}
            for state_path, state_row_iter in self.state_row_iter_dict_by_state_path.iteritems():
                state_row_path = self.tree_store.get_path(state_row_iter)
                act_expansion_state[state_path] = self.view.row_expanded(state_row_path)
                # if act_expansion_state[state_path]:
                #     print state_path
            self.__expansion_state[self.__my_selected_sm_id] = act_expansion_state
        except TypeError:
            logger.debug("expansion state of state machine {0} could not be stored".format(self.__my_selected_sm_id))

    def redo_expansion_state(self):
        if self.__my_selected_sm_id in self.__expansion_state:
            # print "\n\n redo of state machine {0} \n\n".format(self.__my_selected_sm_id)
            try:
                for state_path, state_row_expanded in self.__expansion_state[self.__my_selected_sm_id].iteritems():
                    state_row_iter = self.state_row_iter_dict_by_state_path[state_path]
                    state_row_path = self.tree_store.get_path(state_row_iter)
                    if state_row_expanded:
                        self.view.expand_to_path(state_row_path)
                        # print state_path
            except (TypeError, KeyError):
                logger.debug("expansion state of state machine {0} could not be re-done".format(self.__my_selected_sm_id))

    def update(self, changed_state_model=None, with_expand=False):
        """
        Function checks if all states are in tree and if tree has states which were deleted
        :param changed_state_model:
        :return:
        """
        if not self.view_is_registered:
            return

        # define initial state-model for update
        if not changed_state_model:
            # reset all
            parent_row_iter = None
            self.state_row_iter_dict_by_state_path.clear()
            self.tree_store.clear()
            if self._selected_sm_model:
                changed_state_model = self._selected_sm_model.root_state
            else:
                return
        else:  # pick
            if changed_state_model.state.is_root_state:
                parent_row_iter = self.state_row_iter_dict_by_state_path[changed_state_model.state.get_path()]
            else:
                parent_row_iter = self.state_row_iter_dict_by_state_path[changed_state_model.parent.state.get_path()]

        # do recursive update
        self.insert_and_update_rec(parent_row_iter, changed_state_model, with_expand)

    def update_tree_store_row(self, state_model):
        state_row_iter = self.state_row_iter_dict_by_state_path[state_model.state.get_path()]
        # print "\n\n####### 1 ######## {0}".format(state_row_iter)
        # print "check for update row of state: ", state_model.state.get_path()
        state_row_path = self.tree_store.get_path(state_row_iter)

        if not type(state_model.state) == self.tree_store[state_row_path][2] or \
                not state_model.state.name == self.tree_store[state_row_path][0]:
            # print "update row of state: ", state_model.state.get_path()
            self.tree_store[state_row_path][0] = state_model.state.name
            self.tree_store[state_row_path][2] = type(state_model.state)
            self.tree_store[state_row_path][3] = state_model
            self.tree_store.row_changed(state_row_path, state_row_iter)

    def insert_and_update_rec(self, parent_iter, state_model, with_expand=False):
        # check if in
        state_path = state_model.state.get_path()
        if state_path not in self.state_row_iter_dict_by_state_path:
            # if not in -> insert it
            state_row_iter = self.tree_store.insert_before(parent=parent_iter, sibling=None,
                                                           row=(state_model.state.name,
                                                                state_model.state.state_id,
                                                                type(state_model.state),
                                                                state_model,
                                                                state_model.state.get_path()))
            self.state_row_iter_dict_by_state_path[state_path] = state_row_iter
            if with_expand:
                parent_path = self.tree_store.get_path(state_row_iter)
                self.view.expand_to_path(parent_path)
        else:
            # if in -> check if up to date
            state_row_iter = self.state_row_iter_dict_by_state_path[state_model.state.get_path()]
            self.update_tree_store_row(state_model)

        # check children
        # - check if ALL children are in
        if type(state_model) is ContainerStateModel:
            for child_state_id, child_state_model in state_model.states.items():
                self.insert_and_update_rec(state_row_iter, child_state_model, with_expand=False)

        # - check if TOO MUCH children are in
        for n in reversed(range(self.tree_store.iter_n_children(state_row_iter))):
            child_iter = self.tree_store.iter_nth_child(state_row_iter, n)
            # check if there are left over rows of old states (switch from HS or CS to S and so on)
            if not type(state_model) is ContainerStateModel or not self.tree_store.get_value(child_iter, 1) in state_model.states:
                del self.state_row_iter_dict_by_state_path[self.tree_store.get_value(child_iter, 4)]
                self.tree_store.remove(child_iter)

    def on_cursor_changed(self, widget):
        (model, row) = self.view.get_selection().get_selected()
        logger.debug("The view jumps to the selected state and the zoom should be adjusted as well")
        if row is not None and not self.no_cursor_selection:
            state_model = model[row][3]
            self._selected_sm_model.selection.clear()

            state_row_path = self.tree_store.get_path(self.state_row_iter_dict_by_state_path[model[row][4]])
            self.view.expand_to_path(state_row_path)

            self._selected_sm_model.selection.add(state_model)

    @ExtendedController.observe("selection", after=True)
    def assign_notification_selection(self, model, prop_name, info):
        if self._selected_sm_model.selection.get_selected_state():

            # # work around to avoid already selected but not insert state rows
            # if not self._selected_sm_model.selection.get_selected_state().state.get_path() in self.path_store:
            #     self.update(self._selected_sm_model.root_state)

            (model, actual_iter) = self.view.get_selection().get_selected()
            selected_iter = self.state_row_iter_dict_by_state_path[self._selected_sm_model.selection.get_selected_state().state.get_path()]
            # logger.debug("TreeSelectionPaths actual %s and in state_machine.selection %s " % (actual_iter, selected_iter))
            # print "\n\n####### 3 ########\n\n"
            selected_path = self.tree_store.get_path(selected_iter)
            if actual_iter is None:
                actual_path = None
            else:
                # print "\n\n####### 4 ########\n\n"
                actual_path = self.tree_store.get_path(actual_iter)
            # logger.debug("TreeSelectionPaths actual %s and in state_machine.selection %s " % (actual_path, selected_path))
            if not selected_path == actual_path:
                # logger.debug("reselect state machine tree-selection")
                # if single selection-mode is set no un-select is needed
                #self.view.get_selection().unselect_path(actual_path)
                # self.no_cursor_selection = True
                self.view.expand_to_path(selected_path)
                self.view.get_selection().select_iter(selected_iter)
                # self.no_cursor_selection = False

                # # work around to force selection to state-editor
                # self._selected_sm_model.selection.set([self._selected_sm_model.selection.get_selected_state()])
