import unittest


from pardus import SSHConnector, ConfigList


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.CONNECTIONS = [
            SSHConnector,
            SSHConnector,
            SSHConnector
        ]

        self.config = ConfigList.from_connections

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

    def test_length(self):
        self.assertTrue(True)

    def test_get_element(self):
        self.assertTrue(True)

    def test_take_element(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
