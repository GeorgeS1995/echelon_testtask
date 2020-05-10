import json
import ipaddress
import logging
from api.cmd_network_setting import CmdNetworkSetting

lh = logging.getLogger('root')


class Filehandler:
    def update_db(self, result, path):
        with open(path, 'r+') as db:
            try:
                db_map = json.load(db)
            except json.JSONDecodeError:
                lh.warning("Can't serialize info from db")
                json.dump(result, db)
                return result
        for k, v in result.items():
            try:
                network = CmdNetworkSetting.netmask_to_cidr(v['list_ipv4'][0], v['subnet_mask'])
            except IndexError:
                continue
            network = ipaddress.ip_network(network)
            try:
                for ip in db_map[k]['list_ipv4']:
                    if ipaddress.ip_address(ip) in network and ip not in result[k]['list_ipv4']:
                        result[k]['list_ipv4'].append(ip)
            except KeyError:
                pass
        with open(path, 'w') as db:
            json.dump(result, db)
        return result

    def add_to_db(self, db_map, added_ip, path):
        adapter_with_added_ip = []
        not_in_adapter_network = []
        added = False
        for k, v in db_map.items():
            try:
                network = CmdNetworkSetting.netmask_to_cidr(v['list_ipv4'][0], v['subnet_mask'])
            except IndexError:
                continue
            network = ipaddress.ip_network(network)
            if added_ip in v['list_ipv4']:
                adapter_with_added_ip.append(k)
                continue
            if ipaddress.ip_address(added_ip) in network:
                db_map[k]['list_ipv4'].append(added_ip)
                added = True
                continue
            not_in_adapter_network.append(k)
        if added:
            with open(path, 'w') as db:
                json.dump(db_map, db)
                return adapter_with_added_ip, not_in_adapter_network, added
        return adapter_with_added_ip, not_in_adapter_network, added

    def delet_from_db(self, db_map, added_ip, path):
        was_removed = False
        for k in db_map.keys():
            try:
                db_map[k]['list_ipv4'].remove(added_ip)
                was_removed = True
            except ValueError:
                continue

        with open(path, 'w') as db:
            json.dump(db_map, db)
        return was_removed
