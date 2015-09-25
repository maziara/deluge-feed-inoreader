from . import config
from deluge_client import DelugeRPCClient

########################################################
###########        Deluge Methods       ################
########################################################

def connect_to_deluge():
    client = DelugeRPCClient(config.DLGD_HOST, config.DLGD_PORT, config.DLGD_USER, config.DLGD_PASS)
    client.connect()
    if client.connected: print "Connected to daemon"

    from types import MethodType
    def add_torr_url(self, url):
        return self.call('core.add_torrent_url', url, {})
    client.add_torr_url = MethodType(add_torr_url, client, DelugeRPCClient)

    return client

########################################################

