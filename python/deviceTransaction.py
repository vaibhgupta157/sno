from netconf.client import NetconfSSHSession
from ncclient import manager
#from rollback import Rollback



class Device:

    def __init__(self, device):
        self.device = device
        self.session = None

    def connect(self):
        host = str(self.device.mgmt_ip)
        port = int(self.device.netconf_port)
        username = str(self.device.netconf_user)
        password = str(self.device.netconf_password)
        if not self.session:
            #self.session = NetconfSSHSession(host, port, username, password)
            self.session = manager.connect(host=host, port=port, username=username, password=password, hostkey_verify=False, look_for_keys=False, device_params={'name':'default'})

    def get_config(self, source="running"):
        if not self.session:
            self.connect()
        return self.session.get_config(source=source)
    
    def edit_config(self, config):
        if not self.session:
            self.connect()
        self.session.edit_config(target='candidate', config=config)

    def discard_changes(self):
        if not self.session:
            self.connect()
        self.session.discard_changes()

    def commit(self):
        if not self.session:
            self.connect()
        self.session.commit()

    def close_session(self):
        if not self.session:
            return
        self.session.close_session()

    
def NetworkTransaction(device_config, snoRoot):


    edited_device_list = []
    for device_name in device_config.keys():
        device = snoRoot.devices.device[device_name]
        DevTransaction = Device(device)
        try:
            DevTransaction.edit_config(device_config[device_name]['config'])
        except Exception as e:
            for edited_device in edited_device_list:
                new_transaction = Device(edited_device)
                new_transaction.discard_changes()
            raise Exception(e)
        edited_device_list.append(device)

    committed_device_list = []
    for device_name in device_config.keys():
        device = snoRoot.devices.device[device_name]
        DevTransaction = Device(device)
        try:
            DevTransaction.commit()
        except Exception as e:
            for committed_device in committed_device_list:
                new_transaction = Device(committed_device)
                new_transaction.edit_config(device_config[device_name]['rev_config'])
                new_transaction.commit()
            raise Exception(e)
        committed_device_list.append(device)
