import subprocess
from flask.views import MethodView
import logging
from flask import make_response, current_app, request
import json
from .cmd_network_setting import CmdNetworkSetting
from .exception import UnsupportedOSError, IpFormatError
from .filehandler import Filehandler

lh = logging.getLogger('root')
cmd = CmdNetworkSetting()


def deserialize_json(raw_data):
    try:
        deserialized_data = json.loads(raw_data)
    except json.JSONDecodeError:
        raise
    try:
        added_ip = deserialized_data['ipv4']
        if not CmdNetworkSetting.ip_patter_v4.search(added_ip):
            raise IpFormatError
    except KeyError:
        raise
    leading_removed = list(map(lambda oct: oct.lstrip("0") if oct.lstrip("0") else "0", added_ip.split(".")))
    return ".".join(leading_removed)


class NetworkMethodView(MethodView):
    def __init__(self):
        super().__init__()
        self.path_db = current_app.config['DB_FILE_PATH']
        self.db = Filehandler()

    def get(self):
        try:
            result = cmd.read_setting()
        except subprocess.CalledProcessError as err:
            msg = f"Сan't get information about adapters {err}"
            lh.error(msg)
            return make_response(({'error': msg}, 500))
        except UnsupportedOSError as err:
            lh.error(err)
            return make_response(({'error': f'{err}'}, 500))
        return make_response((result, 200))

    def post(self):
        try:
            added_ip = deserialize_json(request.data)
        except json.JSONDecodeError as err:
            lh.error(err)
            return make_response(({'error': err}, 500))
        except IpFormatError as err:
            lh.error(err)
            return make_response(({'error': f'{err}'}, 400))
        except KeyError:
            msg = f"Wrong json format"
            lh.error(msg)
            return make_response(({'error': msg}, 400))

        try:
            result = cmd.read_setting()
        except subprocess.CalledProcessError as err:
            msg = f"Сan't get information about adapters {err}"
            lh.error(msg)
            return make_response(({'error': msg}, 500))
        except UnsupportedOSError as err:
            lh.error(err)
            return make_response(({'error': err}, 500))

        db_map = self.db.update_db(result, self.path_db)

        adapter_with_added_ip, not_in_adapter_network, added = self.db.add_to_db(db_map, added_ip, self.path_db)

        if added:
            return "", 201
        if adapter_with_added_ip:
            lh.error(f'ip is already on the list of adapters: {";".join(adapter_with_added_ip)}')
        if not_in_adapter_network:
            lh.error(f'ip is not in the adapter subnet: {";".join(not_in_adapter_network)}')
        return make_response(({'error': 'ip is not in the adapter subnet or'
                                        ' ip is already on the list of adapters'}, 400))

    def delete(self):
        try:
            added_ip = deserialize_json(request.data)
        except json.JSONDecodeError as err:
            lh.error(err)
            return make_response(({'error': err}, 500))
        except IpFormatError as err:
            lh.error(err)
            return make_response(({'error': err}, 400))
        except KeyError:
            msg = f"Wrong json format"
            lh.error(msg)
            return make_response(({'error': msg}, 400))

        try:
            result = cmd.read_setting()
        except subprocess.CalledProcessError as err:
            msg = f"Сan't get information about adapters {err}"
            lh.error(msg)
            return make_response(({'error': msg}, 500))
        except UnsupportedOSError as err:
            lh.error(err)
            return make_response(({'error': err}, 500))

        db_map = self.db.update_db(result, self.path_db)

        if self.db.delet_from_db(db_map, added_ip, self.path_db):
            return "", 204
        return make_response(({'error': 'ip is not in the db'}, 404))
