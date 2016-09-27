import config
import requests
import re
import urllib2
from bs4 import BeautifulSoup
from datetime import datetime


########################################################
###########            Globals          ################
########################################################

payload     = {}
config.INO_APP_ID  = "1000001210"
config.INO_APP_KEY = "mW9JK95jWm80bcC1KjnHHKcQpUm_usrk"
config.INO_API_END = "https://www.inoreader.com/reader/api/0/"


########################################################
###########      InoReader Methods      ################
########################################################

def signin():
    global payload
    url = 'https://www.inoreader.com/accounts/ClientLogin'
    payload = {'Email': config.INO_USR, 'Passwd': config.INO_PSW}
    r = requests.post(url, data=payload)
    if r.status_code == 200:
        GAUTH = re.search('(?<=Auth=).*', r.content).group(0)
        payload = {'AppId': config.INO_APP_ID, 'AppKey': config.INO_APP_KEY, 'Authorization': 'GoogleLogin auth=' + GAUTH}
        print "Inoreader signed in successfully"
        return payload
    else:
        print "Signin failed: " + r.text
        return {}

def do_post(term, data={}):
    r = requests.post(config.INO_API_END + term, headers=payload, data=data)
    if r.status_code == 200:
        return r
    else:
        print "Error: " + r.text
        raise

def do_get(term, data={}):
    r = requests.post(config.INO_API_END + term, headers=payload, data=data)
    if r.status_code == 200:
        return r
    else:
        print "Error: " + r.text
        raise
    
def get_all_tags():
    r = do_post('tag/list')
    print r.content

def get_starred_items():
    r = do_post('stream/contents/user/-/state/com.google/starred')
    result = r.json()
    # for item in result['items']:
    #     print item['title']
    return result

def get_downloadable_items():
    r = do_post('stream/contents/' + config.DOWNLOAD_LABEL)
    result = r.json()
    return result
    
def get_unread_items():
    params = {'xt': 'user/-/state/com.google/read'} #Don't get the read ones
    params['n'] = 1000                                #Get 100 articles
    params['r'] = 'o'                               #Sort by olderst first
    folder = 'user/-/label/P'                      #Only articles from this folder
    r = do_post('stream/contents/' + folder, data = params)
    result = r.json()
    #print_items(result['items'])
    return result
    
def get_unseeded_items():
    params = {'n': 1000}                             #Get 100 articles
    params['r'] = 'o'                               #Sort by olderst first
    folder = config.NO_SEED_LABEL                   #Only unseeded articles
    r = do_post('stream/contents/' + folder, data = params)
    result = r.json()
    #print_items(result['items'])
    return result
    
def print_items(items):
    for i in items:
        try:
            print(i['origin']['title'], i['title'], get_seeder_count(i))
        except:
            print("Failed seedcount for:" + i['title'])
            continue
    
def get_enclosure_url(item):
    return str(item['enclosure'][0]['href'].encode('utf8'))
    
def download_enclosure(item):
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = {'User-Agent': user_agent}
    data = ""
    url = get_enclosure_url(item)
    req = urllib2.Request(url, data, headers)
    
    # Open the url
    try:
        filename = 'torrent_file.torrent'
        response = urllib2.urlopen(req)
        print "downloading " + url

        # Open our local file for writing
        with open(filename, "wb") as local_file:
            local_file.write(response.read())
        return filename
    #handle errors
    except urllib2.HTTPError, e:
        print "HTTP Error:", e.code, url
        raise
    except urllib2.URLError, e:
        print "URL Error:", e.reason, url
        raise    
    
def get_item_url(item):
    return item['alternate'][0]['href']
    
def get_item_page(item):
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = {'User-Agent': user_agent}
    data = ""
    url = get_item_url(item)
    req = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(req)
    soup = BeautifulSoup(response.read(), "lxml")
    return soup
    
def get_seeder_count(item):
    page = get_item_page(item)
    seeds_tag = page.find('span', 'seed')
    if (seeds_tag):
        return int(seeds_tag.text)
    else:
        return 0

def get_labels(item):
    #Get the list of labels on an item. 
    #So far we just use one label for each item.
    # Need to be expanded later
    return [ label_url_to_name(c) for c in item['categories']]
    
def published_time(item):
    return datetime.fromtimestamp(int(item["published"]))

def updated_time(item):
    return datetime.fromtimestamp(int(item["updated"]))
    
def is_newer(item, thedate):
    itempdate = published_time(item)
    itemudate = updated_time(item)
    return (itempdate >= thedate or itemudate >= thedate)
    
def has_label(label, item):
    if label in get_labels(item):
        return True
    else:
        return False

def label_url_to_name(label):
    m = re.search('(?<=label/).*', label)
    if m:
        return m.group(0)
    
def generate_save_path(item):
    labels = get_labels(item)
    if len(labels) > 0:
        label = labels[3] + '/'
    else:
        label = ""
    return config.DOWNLOAD_BASE_FOLDER + label + item['origin']['title']

def change_items_labels(item_ids, add='', rem=''):
    ### For Some reason the last item in the post always gets ignored. 
    ### So we add a dummy END value to the list.
    ### ToDo for later
    if isinstance(item_ids, type([])): 
        params = {'i': item_ids + ["END"]}
    else:
        params = {'i': item_ids}
    if add: params['a'] = add
    if rem: params['r'] = rem
    do_post('edit-tag', data = params)
    
def toggle_labels(item_ids):
    if len(item_ids) > 0:
        print "Saved " + str(len(item_ids)) + " items."
        change_items_labels(item_ids, rem=config.DOWNLOAD_LABEL, add=config.ARCHIVE_LABEL)

def mark_seeded(item_ids):
    change_items_labels(item_ids, rem=config.NO_SEED_LABEL ,add=config.HAS_SEED_LABEL)
def mark_unseeded(item_ids):
    change_items_labels(item_ids, add=config.NO_SEED_LABEL)

def mark_as_read(item_ids):
    change_items_labels(item_ids, add='user/-/state/com.google/read')
def mark_as_unread(item_ids):
    change_items_labels(item_ids, rem='user/-/state/com.google/read')

### Sign in upon module import
### You can comment this out and sign in manually
signin()


