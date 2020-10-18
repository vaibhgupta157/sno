from netconf.client import NetconfSSHSession
from ncclient import manager



class Device:

    def __init__(self, device):
        self.device = device
        self.session = None

    def connect(self):
        host = self.device.mgmt_ip
        port = self.device.netconf_port
        username = self.device.netconf_user
        password = self.device.netconf_password
        if not self.session:
            #self.session = NetconfSSHSession(host, port, username, password)
            self.session = manager.connect(host=host, port=port, username=username, password=password, hostkey_verify=False, look_for_keys=False)

    def get_config(self):
        if not self.session:
            self.connect()
        return self.session.get_config("running")
    
    def edit_config(self, config):
        if not self.session:
            self.connect()
        self.session.edit_config(target='candidate', newconf=config)

    def commit(self):
        if not self.session:
            self.connect()
        self.session.commit()

    
def NetworkTransaction(device_config, snoRoot):

    for device_name in device_config.keys():
        device = snoRoot.devices.device[device_name]
        DevTransaction = Device(device)
        DevTransaction.edit_config(device_config[device_name])

    for device_name in device_config.keys():
        DevTransaction = Device(device)
        DevTransaction.commit()