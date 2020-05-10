import re
import subprocess
import sys
import chardet
from .exception import UnsupportedOSError


class CmdNetworkSetting:
    ip_patter_v4 = re.compile(
        r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
    ip_patter_v6 = re.compile(
    r"(?:(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){6})(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):(?:(?:[0-9a-fA-F]{1,4})))|"
    r"(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|"
    r"(?:(?:::(?:(?:(?:[0-9a-fA-F]{1,4})):){5})(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):(?:(?:[0-9a-fA-F]{1,4})))|"
    r"(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|"
    r"(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})))?::(?:(?:(?:[0-9a-fA-F]{1,4})):){4})(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):"
    r"(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|"
    r"(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){0,1}(?:(?:[0-9a-fA-F]{1,4})))?::"
    r"(?:(?:(?:[0-9a-fA-F]{1,4})):){3})(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):(?:(?:[0-9a-fA-F]{1,4})))|"
    r"(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|"
    r"(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){0,2}(?:(?:[0-9a-fA-F]{1,4})))?::(?:(?:(?:[0-9a-fA-F]{1,4})):){2})"
    r"(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|"
    r"(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|"
    r"(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){0,3}(?:(?:[0-9a-fA-F]{1,4})))?::(?:(?:[0-9a-fA-F]{1,4})):)"
    r"(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):(?:(?:[0-9a-fA-F]{1,4})))|"
    r"(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|"
    r"(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){0,4}(?:(?:[0-9a-fA-F]{1,4})))?::)(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):"
    r"(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}"
    r"(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){0,5}"
    r"(?:(?:[0-9a-fA-F]{1,4})))?::)(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){0,6}"
    r"(?:(?:[0-9a-fA-F]{1,4})))?::))))"
    )
    linux_int_patter = re.compile(r"[\d]+: ([\w-]+):")
    linux_v4_patter = re.compile(
        r"inet (?P<addr>(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))/"
        r"(?P<mask>[\d]{1,2})"
    )
    linux_v4_gateway = re.compile(
    r"default via (?P<addr>(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))"
    r" dev (?P<interface>[\w]+) "
    )

    # Netifaces or psutil can be used to determine network parameters
    def _parse_windows_network_setting(self, string):
        res = {}
        strings = string.split("\r\n")
        cur_adapter = ''
        for string in strings:
            if not string.startswith(" ") and string.endswith(":"):
                cur_adapter = string[:-1]
                res[cur_adapter] = {}
                res[cur_adapter]['list_ipv4'] = []
                res[cur_adapter]['list_ipv6'] = []
                continue
            regex_ipv4 = CmdNetworkSetting.ip_patter_v4.search(string)
            if regex_ipv4:
                res[cur_adapter]['list_ipv4'].append(regex_ipv4.group(0))
                continue
            regex_ipv6 = CmdNetworkSetting.ip_patter_v6.search(string)
            if regex_ipv6:
                res[cur_adapter]['list_ipv6'].append(regex_ipv6.group(0))
                continue
        for k, v in res.items():
            if v['list_ipv4']:
                res[k]['gateway'] = v['list_ipv4'].pop()
                res[k]['subnet_mask'] = v['list_ipv4'][1]
                res[k]['list_ipv4'] = [i for j, i in enumerate(res[k]['list_ipv4']) if j % 2 == 0]
        return res

    def _cidr_to_netmask(self, cidr):
        cidr = int(cidr)
        mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
        return (str((0xff000000 & mask) >> 24) + '.' +
                str((0x00ff0000 & mask) >> 16) + '.' +
                str((0x0000ff00 & mask) >> 8) + '.' +
                str((0x000000ff & mask)))

    def _parse_linux_network_setting(self, string):
        strings = string.split("\n")
        res = {}
        cur_adapter = ''
        for string in strings:
            regex_interface = CmdNetworkSetting.linux_int_patter.search(string)
            if regex_interface:
                cur_adapter = regex_interface.group(1)
                res[cur_adapter] = {}
                res[cur_adapter]['list_ipv4'] = []
                res[cur_adapter]['list_ipv6'] = []
                continue
            regex_ipv4 = CmdNetworkSetting.linux_v4_patter.search(string)
            if regex_ipv4:
                addr_par = regex_ipv4.groupdict()
                res[cur_adapter]['list_ipv4'].append(addr_par['addr'])
                res[cur_adapter]['subnet_mask'] = self._cidr_to_netmask(addr_par['mask'])
                continue
            regex_ipv6 = CmdNetworkSetting.ip_patter_v6.search(string)
            if regex_ipv6:
                res[cur_adapter]['list_ipv6'].append(regex_ipv6.group(0))
                continue
            regex_gateway = CmdNetworkSetting.linux_v4_gateway.search(string)
            if regex_gateway:
                gateway = regex_gateway.groupdict()
                res[gateway['interface']]['gateway'] = gateway['addr']
        return res

    def read_setting(self):
        system = sys.platform
        if system == 'win32':
            try:
                out = subprocess.run(["ipconfig"], capture_output=True, check=True)
                enc_param = chardet.detect(out.stdout)
                out = out.stdout.decode(enc_param['encoding'])
            except subprocess.CalledProcessError:
                raise
            result = self._parse_windows_network_setting(out)
        elif system == 'linux':
            try:
                out = subprocess.run(["ip", "a"], capture_output=True, check=True, universal_newlines=True)
                string = out.stdout
            except subprocess.CalledProcessError:
                raise
            try:
                out = subprocess.run(["ip", "r"], capture_output=True, check=True, universal_newlines=True)
                string += f'\n{out.stdout}'
            except subprocess.CalledProcessError:
                raise
            result = self._parse_linux_network_setting(string)
        else:
            raise UnsupportedOSError
        return result

    @staticmethod
    def netmask_to_cidr(ip, mask):
        masksplit = list(map(lambda x: int(x), mask.split(".")))
        ipsplit = list(map(lambda x: int(x), ip.split(".")))
        cidr = (sum(bin(bits).count("1") for bits in masksplit))
        network = []
        for m_octet, ip_octet in zip(masksplit, ipsplit):
            network.append(str(m_octet & ip_octet))
        return f'{".".join(network)}/{cidr}'
