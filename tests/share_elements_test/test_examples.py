import os
from os.path import join
import sys
import time
import threading
import subprocess

# core elements
import rafcon.core.singleton
from rafcon.core.storage import storage

# gui elements
import rafcon

# general tool elements
from rafcon.utils import log

# test environment elements
import testing_utils
import pytest

logger = log.get_logger(__name__)
# TODO move this test in a separate shared element test folder


def shutdown_gui(duration_wait_for_gui):
    # wait for menu bar and main window controller
    menubar_ctrl = None
    time.sleep(2)
    while menubar_ctrl is None:
        time.sleep(duration_wait_for_gui)
        menubar_ctrl = rafcon.gui.singleton.main_window_controller.get_controller('menu_bar_controller') if \
            rafcon.gui.singleton.main_window_controller else None

    # quit rafcon by menu bar
    testing_utils.call_gui_callback(menubar_ctrl.on_save_as_activate, None, None,
                                    testing_utils.get_unique_temp_path())
    testing_utils.call_gui_callback(menubar_ctrl.on_stop_activate, None)
    testing_utils.call_gui_callback(menubar_ctrl.on_quit_activate, None)


def test_api_example(caplog):

    path_of_api_examples = os.path.join(testing_utils.EXAMPLES_PATH, 'api', 'generate_state_machine')
    sys.path.insert(0, path_of_api_examples)

    testing_utils.test_multithreading_lock.acquire()
    try:
        import basic_turtle_state_machine
        # TODO maybe extend example to run ros processes to check functionality of state machine too
        duration_wait_for_gui = 0.1
        timed_thread = threading.Timer(5*duration_wait_for_gui, shutdown_gui, args=[duration_wait_for_gui,])
        timed_thread.daemon = True
        timed_thread.start()

        basic_turtle_state_machine.run_turtle_demo()
        logger.debug("after gtk main")
        timed_thread.join()
    finally:
        sys.path.remove(path_of_api_examples)
        testing_utils.shutdown_environment(caplog=caplog, expected_warnings=0, expected_errors=0)


def test_ros_library_examples(caplog):
    """This test checks whether all ros example libraries are functional"""
    # TODO implement the tests


def test_turtle_library_examples(caplog):
    """This test checks whether all turtle example libraries are functional"""
    # TODO implement the tests


def test_functionality_example(caplog):
    """Test for now only tests:
    - if the state machine can be open
    - if test can be run and stopped
    - and everything can be closed again
    """

    # The test maybe should also test if functionality are correct depicted.
    # TODO check if this is done in the common tests already

    for name in ['backward_step_barrier', 'backward_step_hierarchy', 'backward_step_preemption', 'decider_statemachine',
                 'hierarchy_abortion_handling']:
        sm_path = join(testing_utils.EXAMPLES_PATH, 'functionality_examples', name)
        print sm_path
        state_machine = storage.load_state_machine_from_path(sm_path)
        rafcon.core.singleton.state_machine_manager.add_state_machine(state_machine)

    testing_utils.test_multithreading_lock.acquire()
    try:
        # main_window_controller = rafcon.gui.singleton.main_window_controller
        for state_machine_id in rafcon.core.singleton.state_machine_manager.state_machines.keys():
            rafcon.core.singleton.state_machine_manager.active_state_machine_id = state_machine_id
            rafcon.core.singleton.state_machine_execution_engine.start()
            time.sleep(3)
            rafcon.core.singleton.state_machine_execution_engine.stop()
            rafcon.core.singleton.state_machine_execution_engine.join()
    finally:
        testing_utils.shutdown_environment(gui_config=False, caplog=caplog, expected_warnings=2, expected_errors=3)


def test_plugins_example(caplog):

    os.environ['RAFCON_PLUGIN_PATH'] = os.path.join(testing_utils.EXAMPLES_PATH, 'plugins', 'templates')
    print os.environ.get('RAFCON_PLUGIN_PATH')
    # testing_utils.initialize_environment()
    testing_utils.test_multithreading_lock.acquire()
    try:
        cmd = join(testing_utils.RAFCON_PATH, 'gui', 'start.py')
        rafcon_gui_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        time.sleep(3)
        rafcon_gui_process.terminate()
        rafcon_gui_process.wait()
        assert rafcon_gui_process.returncode == 0

        process_output, _ = rafcon_gui_process.communicate()

        print '#check if PLUGINS have been run:'
        assert any(["Successfully loaded plugin 'templates'" in line for line in process_output.split('\n')])
        print "#process PID: ", rafcon_gui_process.pid
        # testing_utils.run_gui()
    finally:
        testing_utils.shutdown_environment(caplog=caplog, expected_warnings=0, expected_errors=0)


def test_tutorial_state_machine_examples(caplog):
    """This test checks whether all tutorial state machine example are functional"""
    # TODO implement the tests


if __name__ == '__main__':
    pytest.main([__file__])
