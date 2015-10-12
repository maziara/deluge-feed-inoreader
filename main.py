import inoreaderapi
import delugeapi

def go_process():
    items = inoreaderapi.get_downloadable_items()
    if len(items['items']) == 0:
        print "No items to retreive. Exiting."
    else:
        print "Retreived " + str(len(items['items'])) + " starred items"
        client = delugeapi.connect_to_deluge()
        for item in items['items']:
            print "Saving -> '" + item['title'] + "'"
            tor_id = client.add_torr_url(inoreaderapi.get_enclosure_url(item))
            if tor_id: #URL added, otherwise it's probably already in deluge!
                label = item['origin']['title']

                if not client.label_exist(label):
                    client.add_label(label, {'move_completed_path': inoreaderapi.generate_save_path(item)})

                client.add_tor_label(tor_id, label )

        inoreaderapi.toggle_labels([i['id'] for i in items['items']])

if __name__ == "__main__":
    go_process()