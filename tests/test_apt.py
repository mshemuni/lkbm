import unittest

from pardus import SSHConnector, Apt


class TestApt(unittest.TestCase):

    def setUp(self):
        self.CONNECTION = SSHConnector
        self.APT = Apt

    def test_repositories(self):
        self.assertTrue(True)

    def test_add_repository(self):
        self.assertTrue(True)

    def test_update(self):
        self.assertTrue(True)

    def test_upgrade(self):
        self.assertTrue(True)

    def test_list(self):
        self.assertTrue(True)

    def test_install(self):
        self.assertTrue(True)

    def test_reinstall(self):
        self.assertTrue(True)

    def test_remove(self):
        self.assertTrue(True)

    def test_purge(self):
        self.assertTrue(True)

    def test_search(self):
        self.assertTrue(True)

    def test_show(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
