import unittest
import pyftp


class ArgumentsTests(unittest.TestCase):

    def test_parse_hist_name_without_user(self):
        host_name = 'virt-raspberrypi'
        (h, u, cwd) = pyftp.parse_host(host_name)
        self.assertEqual(host_name, h)
        self.assertTrue(not u or u.isspace())
        self.assertTrue(not cwd or cwd.isspace())

    def test_parse_host_name_by_ip(self):
        host_name = '127.0.0.1'
        (h, u, cwd) = pyftp.parse_host(host_name)
        self.assertEqual(host_name, h)

    def test_parse_host_name_should_get_user(self):
        host_name = 'virt_raspberrypi'
        user = 'pi'
        cwd = '~/tests'
        (actual_host, actual_user, actual_cwd) = pyftp.parse_host("{}@{}:{}".format(user, host_name, cwd))
        self.assertEqual(host_name, actual_host)
        self.assertEqual(user, actual_user)
        self.assertEqual(cwd, actual_cwd)


if __name__ == '__main__':
    unittest.main()
