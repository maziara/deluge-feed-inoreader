import config
from deluge_client import DelugeRPCClient
import werkzeug as wz
import base64

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

    def add_torr_file(self, file):
        f = open(file, 'rb')
        filedump = base64.encodestring(f.read())
        f.close()
        return self.call('core.add_torrent_file', file, filedump, {})
    client.add_torr_file = MethodType(add_torr_file, client, DelugeRPCClient)
    
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

    def session_state(self):
        return self.call('core.get_session_state')
    client.session_state = MethodType(session_state, client, DelugeRPCClient)
    
    def torrent_status(self, tid, fields = {}):
        return self.call('core.get_torrent_status', tid, fields)
    client.torrent_status = MethodType(torrent_status, client, DelugeRPCClient)

    def torrents_status(self, filters = {}, fields = []):
        return self.call('core.get_torrents_status', filters, fields)
    client.torrents_status = MethodType(torrents_status, client, DelugeRPCClient)
    
    def get_finished(self):
        torrs = torrents_status(self)
        for k,v in torrs.items():
            #print(k,v['name'])
            if v['is_finished'] == False:
                #print("Removing unfinished: " + v['name'] + " " + str(v['is_finished']))
                torrs.pop(k)
            elif v['tracker_host'] in config.REMOVE_SEEDS_EXCEPTION_TRACKERS:
                #print("Removing exception_tracker: " + v['name'])
                torrs.pop(k)
            elif not is_all_files_done(v):
                #print("Removing not_all_done: " + v['name'])
                torrs.pop(k)
        return torrs
    client.get_finished = MethodType(get_finished, client, DelugeRPCClient)
    
    def remove_finished(self):
        for k in get_finished(self):
            self.call('core.remove_torrent', k, False)
    client.remove_finished = MethodType(remove_finished, client, DelugeRPCClient)
    
    def is_all_files_done(tor):
        for i in tor['file_progress']:
            if i != 1.0: 
                return False
        return True

    return client

def normalize_label(label):
    return label.replace(' ','_').lower()
