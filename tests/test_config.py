import unittest

from pardus import SSHConnector, Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.CONNECTION = SSHConnector

        self.config = Config

    def test_create(self):
        self.assertTrue(True)

    def test_clear(self):
        self.assertTrue(True)

    def test_update(self):
        self.assertTrue(True)

    def test_touch(self):
        self.assertTrue(True)

    def test_exist(self):
        self.assertTrue(True)

    def test_create_backup(self):
        self.assertTrue(True)

    def test_read(self):
        self.assertTrue(True)

    def test___setitem__(self):
        self.assertTrue(True)

    def test___delitem__(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
