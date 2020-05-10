import json
import os
import unittest
from api.cmd_network_setting import CmdNetworkSetting
from api.filehandler import Filehandler
from api.view import deserialize_json


class CmdNetworkSettingTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.cmd_instance = CmdNetworkSetting()

        self.netmask_to_cidr_input = [
            {"ip": "192.168.0.1", "mask": "255.255.255.0"},
            {"ip": "192.168.0.140", "mask": "255.255.255.128"},
        ]

        self.netmask_to_cidr_output = [
            "192.168.0.0/24",
            "192.168.0.128/25"
        ]

        self.cidr_to_netmask_input = ["2", "8", "16", "32"]
        self.cidr_to_netmask_output = ["192.0.0.0", "255.0.0.0", "255.255.0.0", "255.255.255.255"]

        self.linux_terminal_output_default = "6: eth0: <BROADCAST,MULTICAST,UP> mtu 1500 group default " \
                                             "qlen 1\n    link/ether 50:46:5d:76:70:14\n    inet " \
                                             "192.168.0.10/24 brd 192.168.0.255 scope global dynamic\n     " \
                                             "  valid_lft 1853sec preferred_lft 1853sec\n    inet6 " \
                                             "fe80::145e:3590:55f6:83e3/64 scope link dynamic\n      " \
                                             "valid_lft forever preferred_lft forever\n17: eth1: <> mtu " \
                                             "1500 group default qlen 1\n    link/ether " \
                                             "00:ff:bc:ae:f8:a6\n    inet 169.254.130.104/16 brd " \
                                             "169.254.255.255 scope global dynamic\n       valid_lft " \
                                             "forever preferred_lft forever\n    inet6 " \
                                             "fe80::4013:7a4f:862:8268/64 scope link dynamic\n       " \
                                             "valid_lft forever preferred_lft forever\n18: eth2: <> mtu " \
                                             "2800 group default qlen 1\n    link/ether " \
                                             "3a:78:22:ec:50:62\n1: lo: <LOOPBACK,UP> mtu 1500 group " \
                                             "default qlen 1\n    link/loopback 00:00:00:00:00:00\n    " \
                                             "inet 127.0.0.1/8 brd 127.255.255.255 scope global dynamic\n  " \
                                             "     valid_lft forever preferred_lft forever\n    inet6 " \
                                             "::1/128 scope host dynamic\n       valid_lft forever " \
                                             "preferred_lft forever\nnone default via 192.168.0.1 dev eth0 " \
                                             "proto unspec metric 0\nnone 192.168.0.0/24 dev eth0 proto " \
                                             "unspec metric 256\nnone 192.168.0.10 dev eth0 proto unspec " \
                                             "metric 256\nnone 192.168.0.255 dev eth0 proto unspec metric " \
                                             "256\nnone 224.0.0.0/4 dev eth0 proto unspec metric 256\nnone " \
                                             "255.255.255.255 dev eth0 proto unspec metric 256\nnone " \
                                             "224.0.0.0/4 dev eth1 proto unspec metric 256\nnone " \
                                             "255.255.255.255 dev eth1 proto unspec metric 256\nnone " \
                                             "127.0.0.0/8 dev lo proto unspec metric 256\nnone 127.0.0.1 " \
                                             "dev lo proto unspec metric 256\nnone 127.255.255.255 dev lo " \
                                             "proto unspec metric 256\nnone 224.0.0.0/4 dev lo proto " \
                                             "unspec metric 256\nnone 255.255.255.255 dev lo proto unspec " \
                                             "metric 256\n"

        self.linux_terminal_parse_res = {'eth0': {'list_ipv4': ['192.168.0.10'],
                                                  'list_ipv6': ['fe80::145e:3590:55f6:83e3'],
                                                  'subnet_mask': '255.255.255.0', 'gateway': '192.168.0.1'},
                                         'eth1': {'list_ipv4': ['169.254.130.104'],
                                                  'list_ipv6': ['fe80::4013:7a4f:862:8268'],
                                                  'subnet_mask': '255.255.0.0'},
                                         'eth2': {'list_ipv4': [], 'list_ipv6': []},
                                         'lo': {'list_ipv4': ['127.0.0.1'], 'list_ipv6': ['::1'],
                                                'subnet_mask': '255.0.0.0'}}

        # test multiple ipv4 in one interface
        self.linux_terminal_output_multiple_ip = "2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 " \
                                                 "qdisc pfifo_fast state UP group default qlen 1000\n     " \
                                                 "        link/ether 08:00:27:12:f8:c1 brd " \
                                                 "ff:ff:ff:ff:ff:ff\n             inet 192.168.1.105/24 " \
                                                 "brd 192.168.1.255 scope global enp0s3\n              " \
                                                 "valid_lft forever preferred_lft forever\n inet " \
                                                 "192.168.2.105/24 scope global enp0s3\n valid_lft " \
                                                 "forever preferred_lft foreve\nr inet6 " \
                                                 "fe80::a00:27ff:fe12:f8c1/64 scope link\n valid_lft " \
                                                 "forever preferred_lft forever\n "

        self.linux_terminal_parse_res_multiple_ip = {
            'enp0s3': {'list_ipv4': ['192.168.1.105', '192.168.2.105'], 'list_ipv6': ['fe80::a00:27ff:fe12:f8c1'],
                       'subnet_mask': '255.255.255.0'}
        }

        self.windows_cmd_output_default = "Windows IP Configuration\r\nEthernet adapter Ethernet:\r\n   " \
                                          "Connection-specific DNS Suffix  . : oops\r\nLink-local IPv6 Address . " \
                                          ". . . . : fe80::145e:3590:55f6:83e3%6\r\nIPv4 Address. . . . . . . . " \
                                          ". . . : 192.168.0.10\r\nSubnet Mask . . . . . . . . . . . : " \
                                          "255.255.255.0\r\nDefault Gateway . . . . . . . . . : " \
                                          "192.168.0.1\r\nEthernet adapter Ethernet 2:\r\nMedia State . . . . . " \
                                          ". . . . . . : Media disconnected\r\nConnection-specific DNS Suffix  . " \
                                          ": \r\n "
        self.windows_cmd_default_res = {'Ethernet adapter Ethernet':
                                            {'list_ipv4': ['192.168.0.10'],
                                             'list_ipv6': ['fe80::145e:3590:55f6:83e3'],
                                             'gateway': '192.168.0.1', 'subnet_mask': '255.255.255.0'},
                                        'Ethernet adapter Ethernet 2': {'list_ipv4': [], 'list_ipv6': []}}

        self.windows_cmd_rulocal_output = "Настройка протокола IP для Windows\r\nАдаптер Ethernet Ethernet:\r\n   " \
                                          "DNS-суффикс подключения  . : oops\r\nЛокальный IPv6-адрес канала . " \
                                          ". . . . : fe80::145e:3590:55f6:83e3%6\r\nIPv4-адрес. . . . . . . . " \
                                          ". . . : 192.168.0.10\r\nМаска подсети . . . . . . . . . . . : " \
                                          "255.255.255.0\r\nОсновной шлюз . . . . . . . . . : " \
                                          "192.168.0.1\r\nАдаптер Ethernet Ethernet 2:\r\nСостояние среды . . . . . " \
                                          ". . . . . . : Среда передачи недоступна.\r\nDNS-суффикс подключения  . " \
                                          ": \r\n "

        self.windows_cmd_rulocal_res = {'Адаптер Ethernet Ethernet':
                                            {'list_ipv4': ['192.168.0.10'],
                                             'list_ipv6': ['fe80::145e:3590:55f6:83e3'],
                                             'gateway': '192.168.0.1', 'subnet_mask': '255.255.255.0'},
                                        'Адаптер Ethernet Ethernet 2': {'list_ipv4': [], 'list_ipv6': []}}

        # test multiple ipv4 in one interface
        self.windows_cmd_multiple_ip = "\r\nНастройка протокола IP для Windows\r\n\r\n\r\nАдаптер Ethernet " \
                                       "Ethernet:\r\n\r\n   DNS-суффикс подключения . . . . . :\r\n   Локальный " \
                                       "IPv6-адрес канала . . . : fe80::145e:3590:55f6:83e3%6\r\n   IPv4-адрес. . . . " \
                                       ". . . . . . . . : 192.168.0.10\r\n   Маска подсети . . . . . . . . . . : " \
                                       "255.255.255.0\r\n   IPv4-адрес. . . . . . . . . . . . : 192.168.0.11\r\n   " \
                                       "Маска подсети . . . . . . . . . . : 255.255.255.0\r\n   Основной шлюз. . . . " \
                                       ". . . . . : 192.168.0.1\r\n                                       " \
                                       "\r\nАдаптер Ethernet Ethernet 2:\r\n\r\n   Состояние среды. . " \
                                       ". . . . . . : Среда передачи недоступна.\r\n   DNS-суффикс подключения . . . " \
                                       ". . :\r\n "

        self.windows_cmd_multiple_ip_res = {'Адаптер Ethernet Ethernet':
                                                {'list_ipv4': ['192.168.0.10', '192.168.0.11'],
                                                 'list_ipv6': ['fe80::145e:3590:55f6:83e3'],
                                                 'gateway': '192.168.0.1', 'subnet_mask': '255.255.255.0'},
                                            'Адаптер Ethernet Ethernet 2': {'list_ipv4': [], 'list_ipv6': []}}

    def test_netmask_to_cidr(self):
        for indx, input in enumerate(self.netmask_to_cidr_input):
            res = CmdNetworkSetting.netmask_to_cidr(input['ip'], input['mask'])
            self.assertEqual(res, self.netmask_to_cidr_output[indx])

    def test_cidr_to_netmask(self):
        for indx, input in enumerate(self.cidr_to_netmask_input):
            res = self.cmd_instance._cidr_to_netmask(input)
            self.assertEqual(res, self.cidr_to_netmask_output[indx])

    def test_parse_linux_output(self):
        res = self.cmd_instance._parse_linux_network_setting(self.linux_terminal_output_default)
        self.assertEqual(res, self.linux_terminal_parse_res)

    def test_parse_linux_multiple_ip(self):
        res = self.cmd_instance._parse_linux_network_setting(self.linux_terminal_output_multiple_ip)
        self.assertEqual(res, self.linux_terminal_parse_res_multiple_ip)

    def test_parse_windows_output(self):
        res = self.cmd_instance._parse_windows_network_setting(self.windows_cmd_output_default)
        self.assertEqual(res, self.windows_cmd_default_res)

    def test_parse_windows_ru_local(self):
        res = self.cmd_instance._parse_windows_network_setting(self.windows_cmd_rulocal_output)
        self.assertEqual(res, self.windows_cmd_rulocal_res)

    def test_parse_windows_multiple_ip(self):
        res = self.cmd_instance._parse_windows_network_setting(self.windows_cmd_multiple_ip)
        self.assertEqual(res, self.windows_cmd_multiple_ip_res)


class NetworkMethodViewTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ['FLASK_TEST'] = 'True'
        from api.app import app
        cls.app = app.test_client()

    def setUp(self) -> None:
        if not os.path.exists('db_test.json'):
            open(os.path.abspath('db_test.json'), 'a').close()
        self.url = "http://127.0.0.1:5000/api/v1/network"
        self.db = Filehandler()

        self.bad_key = {
            "bad_key": "192.168.0.11"
        }

        self.bad_ip_format = {
            "ipv4": "192.168.300.11"
        }

        self.ip_with_leading_zero = '{"ipv4": "010.010.000.010"}'

        self.ip_without_leading_zero = '10.10.0.10'

        self.parser_result = {'eth0': {'list_ipv4': ['192.168.0.10'],
                                       'list_ipv6': ['fe80::145e:3590:55f6:83e3'],
                                       'subnet_mask': '255.255.255.0', 'gateway': '192.168.0.1'},
                              'eth1': {'list_ipv4': ['169.254.130.104'],
                                       'list_ipv6': ['fe80::4013:7a4f:862:8268'],
                                       'subnet_mask': '255.255.0.0'},
                              'eth2': {'list_ipv4': [], 'list_ipv6': []},
                              'lo': {'list_ipv4': ['127.0.0.1'], 'list_ipv6': ['::1'],
                                     'subnet_mask': '255.0.0.0'}}

        self.update_db = {'eth0': {'list_ipv4': ['192.168.0.10', '192.168.0.11'],
                                   'list_ipv6': ['fe80::145e:3590:55f6:83e3'],
                                   'subnet_mask': '255.255.255.0', 'gateway': '192.168.0.1'},
                          'eth1': {'list_ipv4': ['169.254.130.104'],
                                   'list_ipv6': ['fe80::4013:7a4f:862:8268'],
                                   'subnet_mask': '255.255.0.0'},
                          'eth2': {'list_ipv4': [], 'list_ipv6': []},
                          'lo': {'list_ipv4': ['127.0.0.1'],
                                 'list_ipv6': ['::1'],
                                 'subnet_mask': '255.0.0.0'}}

        self.multiple_delete = {'eth0': {'list_ipv4': ['192.168.0.10', '192.168.0.11'],
                                         'list_ipv6': ['fe80::145e:3590:55f6:83e3'],
                                         'subnet_mask': '255.255.255.0', 'gateway': '192.168.0.1'},
                                'eth1': {'list_ipv4': ['192.168.0.10', '192.168.0.11'],
                                         'list_ipv6': ['fe80::4013:7a4f:862:8268'],
                                         'subnet_mask': '255.255.255.0'},
                                'eth2': {'list_ipv4': [], 'list_ipv6': []}}

        self.multiple_delete_out = {'eth0': {'list_ipv4': ['192.168.0.10'],
                                             'list_ipv6': ['fe80::145e:3590:55f6:83e3'],
                                             'subnet_mask': '255.255.255.0', 'gateway': '192.168.0.1'},
                                    'eth1': {'list_ipv4': ['192.168.0.10'],
                                             'list_ipv6': ['fe80::4013:7a4f:862:8268'],
                                             'subnet_mask': '255.255.255.0'},
                                    'eth2': {'list_ipv4': [], 'list_ipv6': []}}

    def tearDown(self) -> None:
        os.remove(os.path.join(os.getcwd(), "db_test.json"))

    @classmethod
    def tearDownClass(cls):
        del os.environ['FLASK_TEST']

    def test_allowed_methods(self):
        r = self.app.put(self.url)
        self.assertEqual(r._status, '405 METHOD NOT ALLOWED')
        r = self.app.patch(self.url)
        self.assertEqual(r._status, '405 METHOD NOT ALLOWED')

    def test_deserializer_with_zero(self):
        res = deserialize_json(self.ip_with_leading_zero)
        self.assertEqual(res, self.ip_without_leading_zero)

    def test_post_json_deserialize_err(self):
        r = self.app.post(self.url, data=json.dumps(self.bad_key))
        self.assertEqual(r._status, '400 BAD REQUEST')

    def test_post_ip_format_err(self):
        r = self.app.post(self.url, data=json.dumps(self.bad_ip_format))
        self.assertEqual(r._status, '400 BAD REQUEST')

    def test_update_empty_db(self):
        res = self.db.update_db(self.parser_result, 'db_test.json')
        self.assertEqual(res, self.parser_result)

    def test_update_existing_db(self):
        with open('db_test.json', 'w') as db:
            json.dump(self.parser_result, db)
        res = self.db.update_db(self.update_db, 'db_test.json')
        self.assertEqual(res, self.update_db)

    def test_add_to_db(self):
        now_in_db, not_in_subnet, added = self.db.add_to_db(self.parser_result, '192.168.0.11', 'db_test.json')
        self.assertEqual(not_in_subnet, ['eth1', 'lo'])
        self.assertFalse(now_in_db)
        self.assertTrue(added)
        with open('db_test.json', 'r') as db:
            res = json.load(db)
        self.assertEqual(res, self.update_db)

    def test_add_to_db_now_in_db(self):
        with open('db_test.json', 'w') as db:
            json.dump(self.parser_result, db)
        now_in_db, not_in_subnet, added = self.db.add_to_db(self.parser_result, '127.0.0.1', 'db_test.json')
        self.assertEqual(not_in_subnet, ['eth0', 'eth1'])
        self.assertEqual(now_in_db, ['lo'])
        self.assertFalse(added)
        with open('db_test.json', 'r') as db:
            res = json.load(db)
        self.assertEqual(res, self.parser_result)

    def test_delete_from_db(self):
        with open('db_test.json', 'w') as db:
            json.dump(self.update_db, db)
        res = self.db.delet_from_db(self.update_db, '192.168.0.11', 'db_test.json')
        self.assertTrue(res)
        with open('db_test.json', 'r') as db:
            res = json.load(db)
        self.assertEqual(res, self.parser_result)

    def test_delete_from_db_not_exist(self):
        with open('db_test.json', 'w') as db:
            json.dump(self.update_db, db)
        res = self.db.delet_from_db(self.update_db, '192.168.0.12', 'db_test.json')
        self.assertFalse(res)
        with open('db_test.json', 'r') as db:
            res = json.load(db)
        self.assertEqual(res, self.update_db)

    def test_delete_multiple(self):
        with open('db_test.json', 'w') as db:
            json.dump(self.multiple_delete, db)
        res = self.db.delet_from_db(self.multiple_delete, '192.168.0.11', 'db_test.json')
        self.assertTrue(res)
        with open('db_test.json', 'r') as db:
            res = json.load(db)
        self.assertEqual(res, self.multiple_delete_out)


if __name__ == '__main__':
    unittest.main()
