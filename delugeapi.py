from . import config
from deluge_client import DelugeRPCClient
import werkzeug as wz

########################################################
###########        Deluge Methods       ################
########################################################

def connect_to_deluge():
    client = DelugeRPCClient(config.DLGD_HOST, config.DLGD_PORT, config.DLGD_USER, config.DLGD_PASS)
    client.connect()
    if client.connected: print "Connected to deluge daemon"

    from types import MethodType
    
    def add_torr_url(self, url):
        return self.call('core.add_torrent_url', wz.urls.url_fix(url), {})
    client.add_torr_url = MethodType(add_torr_url, client, DelugeRPCClient)
    
    def add_label(self, label, options={}):
        label = normalize_label(label)
        self.call('label.add', label)
        if options:
            if options['move_completed_path']:
                    options.update({'move_completed': True, 'apply_move_completed': True})
            self.call('label.set_options', label, options)
    client.add_label = MethodType(add_label, client, DelugeRPCClient)
    
    def label_exist(self, label):
        label = normalize_label(label)
        if label in self.list_labels():
            return True
        else:
            return False
    client.label_exist = MethodType(label_exist, client, DelugeRPCClient)            
        
    def list_labels(self):
        return self.call('label.get_labels')
    client.list_labels = MethodType(list_labels, client, DelugeRPCClient)
    
    def add_tor_label(self, tor_id, label):
        return self.call('label.set_torrent', tor_id, normalize_label(label))
    client.add_tor_label = MethodType(add_tor_label, client, DelugeRPCClient)

    return client

def normalize_label(label):
    return label.replace(' ','_').lower()
