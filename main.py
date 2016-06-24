import inoreaderapi
import delugeapi
from datetime import datetime
import os

def go_process():
    items = inoreaderapi.get_downloadable_items()
    print datetime.now().isoformat()
    if len(items['items']) == 0:
        print "No items to retreive. Exiting."
    else:
        print "Retreived " + str(len(items['items'])) + " starred items"
        client = delugeapi.connect_to_deluge()
        for item in items['items']:
            print "Saving -> '" + item['title'].encode('utf-8') + "'"
            try:
                tor_id = client.add_torr_url(inoreaderapi.get_enclosure_url(item))
            except:
                ## Could not add torrent URL directly 
                ## Let's try downloading the file instead.
                try:
                    filename = inoreaderapi.download_enclosure(item)
                except:
                    print "Failed on processing: " + item['title'].encode('ascii', 'ignore')
                    guess_error_reason(item)
                    continue
                else:
                    try:
                        tor_id = client.add_torr_file(filename)
                    except:
                        print "Failed on processing: " + item['title'].encode('ascii', 'ignore')
                        print "Probably already added."
                    finally:
                        os.remove(filename)

            if tor_id: #URL added, otherwise it's probably already in deluge!
                label = item['origin']['title']

                if not client.label_exist(label):
                    client.add_label(label, {'move_completed_path': inoreaderapi.generate_save_path(item)})

                client.add_tor_label(tor_id, label )
            item['saved'] = True
            tor_id = ''
        
        inoreaderapi.toggle_labels([i['id'] for i in items['items'] if i.has_key('saved')])
        
def guess_error_reason(item):
    if not(item.has_key('enclosure')) or inoreaderapi.get_enclosure_url(item) == '':
        print "Item has empty enclosure URL."
        
def process_seed_counts():
    items = inoreaderapi.get_unread_items()
    if len(items['items']) == 0:
        return
    process_items_for_seeds(items)
    seeded_items = [i['id'] for i in items['items'] if i.has_key('seed_count') and i['seed_count'] > 0]
    unseeded_items = [i['id'] for i in items['items'] if i.has_key('seed_count') and i['seed_count'] == 0]
    print(str(len(seeded_items)) + "Seeded items")
    print(str(len(unseeded_items)) + "Unseeded items")
    inoreaderapi.mark_seeded(seeded_items)
    inoreaderapi.mark_unseeded(unseeded_items)
    inoreaderapi.mark_as_read(unseeded_items)
    
def recover_unseeded_items():
    items = inoreaderapi.get_unseeded_items()
    if len(items['items']) == 0:
        return
    process_items_for_seeds(items)
    seeded_items = [i['id'] for i in items['items'] if i.has_key('seed_count') and i['seed_count'] > 0]
    unseeded_items = [i['id'] for i in items['items'] if i.has_key('seed_count') and i['seed_count'] == 0]
    print(str(len(seeded_items)) + " items recovered!")
    print(str(len(unseeded_items)) + " items still unseeded.")
    inoreaderapi.mark_seeded(seeded_items)
    inoreaderapi.mark_as_unread(seeded_items)

def process_items_for_seeds(items):
    for item in items['items']:
        if(inoreaderapi.label_url_to_name(inoreaderapi.config.HAS_SEED_LABEL) in inoreaderapi.get_labels(item)):
            continue
        try:
            seed_count = inoreaderapi.get_seeder_count(item)
            print(item['origin']['title'], item['title'], inoreaderapi.get_seeder_count(item))
            item['seed_count'] = seed_count
        except:
            print("Failed fetching seeds count for: " + item['title'])
            continue
    return items

if __name__ == "__main__":
    go_process()
    if inoreaderapi.config.DO_SEED_TAGGING:
        process_seed_counts()
