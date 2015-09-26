from . import config
from . import inoreaderapi
from . import delugeapi

def go_process():
    items = inoreaderapi.get_downloadable_items()
    client = delugeapi.connect_to_deluge()
    for item in items['items']:
        print "Saving -> '" + item['title'] + "'"
        tor_id = client.add_torr_url(inoreaderapi.get_enclosure_url(item))
        label = item['origin']['title']
        
        if not client.label_exist(label):
            client.add_label(label, {'move_completed_path': inoreaderapi.generate_save_path(item)})
            
        client.add_tor_label(tor_id, label )
    
    inoreaderapi.toggle_labels([i['id'] for i in items['items']])
