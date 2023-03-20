import unittest
from unittest.mock import patch, Mock
from io import StringIO
import time
import os
import shutil
import socket
import random

from main import *


class TestMain(unittest.TestCase):

    def setUp(self):
        # Create logs directory if it does not exist
        if not os.path.exists("logs"):
            os.mkdir("logs")
        
        # Create mock sockets
        self.mock_socket = Mock(spec=socket.socket)
        self.mock_client_socket = Mock(spec=socket.socket)
        self.mock_server_socket = Mock(spec=socket.socket)
        self.mock_socket.return_value = self.mock_socket
        self.mock_client_socket.return_value = self.mock_client_socket
        self.mock_server_socket.return_value = self.mock_server_socket
        
        # Create mock addresses
        self.mock_address = ("localhost", 12345)
        self.mock_client_address = ("localhost", 54321)
        
        # Set up logging
        self.test_vm_id = 0
        self.test_event_type = "test_event"
        self.test_data = "test_data"
        self.test_clock = 10

    def tearDown(self):
        # Remove logs directory
        if os.path.exists("logs"):
            shutil.rmtree("logs")

    def test_generate_action(self):
        # Test that generate_action generates values within the correct range
        for i in range(100):
            action = generate_action()
            self.assertGreaterEqual(action, 1)
            self.assertLessEqual(action, MAX_ACTIONS_PER_CYCLE)

    @patch('socket.socket')
    @patch('builtins.open')
    def test_write_to_log(self, mock_open, mock_socket):
        # Test that write_to_log writes the correct data to the correct file
        mock_file = StringIO()
        mock_open.return_value = mock_file
        vm_id = 0
        event_type = "test_event"
        data = "test_data"
        clock = 10

        write_to_log(vm_id, event_type, data, clock)

        log_file_name = "logs/vm0.log"
        self.assertTrue(os.path.exists(log_file_name))
        with open(log_file_name, "r") as log_file:
            contents = log_file.read()
            self.assertIn(event_type, contents)
            self.assertIn(str(vm_id), contents)
            self.assertIn(data, contents)
            self.assertIn(str(clock), contents)

    @patch('socket.socket')
    def test_run_virtual_machine(self, mock_socket):
        # Test that run_virtual_machine sends and receives messages as expected
        # and that internal events are generated
        vm_id = 0
        # Set up mock sockets
        mock_first_socket = Mock(spec=socket.socket)
        mock_second_socket = Mock(spec=socket.socket)
        mock_socket.side_effect = [self.mock_server_socket, self.mock_client_socket, self.mock_client_socket,
                                   self.mock_client_socket, self.mock_server_socket, self.mock_client_socket,
                                   mock_first_socket, self.mock_client_socket, mock_second_socket,
                                   self.mock_client_socket, self.mock_server_socket, self.mock_client_socket]

        # Set up event queue
        self.mock_client_socket.recv.return_value = "1,0,9".encode('utf-8')
        event_queue = [["1", "0", "9"]]
        internal_clock = 0

        # Set up end time
        end_time = time.time() + DURATION_SECONDS

        # Run virtual machine
        run_virtual_machine(vm_id)

        # Assert that messages were sent and received as expected
        self.mock_server_socket.bind.assert_called_once_with(("localhost", PORTS[vm_id]))
        self.mock_server_socket.listen.assert_called_once_with()
        self.mock
