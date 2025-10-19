import unittest

from utils.path_analyst import *


class MyTestCase(unittest.TestCase):
    def test_is_folder(self):
        self.assertTrue(is_folder('/home/user/test/'))
        self.assertTrue(is_folder('/home/user/test/test'))
        self.assertTrue(is_folder('/home/user/test/test\\'))
        self.assertFalse(is_folder('/home/user/test/test.txt'))


if __name__ == '__main__':
    unittest.main()
