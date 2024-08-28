import unittest

from pardus import SSHConnector


class TestConnection(unittest.TestCase):
    def setUp(self):
        self.CONNECTION = SSHConnector

    def test_run(self):
        self.assertTrue(True)

    def test_sudo_run(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
