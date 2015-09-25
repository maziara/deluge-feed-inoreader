from . import config
import requests
import re

########################################################
###########            Globals          ################
########################################################

payload     = {}

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
        print "Signed in Successfully"
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

def get_all_tags():
    r = do_post('tag/list')
    print r.content

def get_starred_items():
    r = do_post('stream/contents/user/-/state/com.google/starred')
    result = r.json()
    print "Retreived " + str(len(result['items'])) + " starred items"
    # for item in result['items']:
    #     print item['title']
    return result

def get_downloadable_items():
    r = do_post('stream/contents/' + config.DOWNLOAD_LABEL)
    result = r.json()
    print "Retreived " + str(len(result['items'])) + " starred items"
    return result
    
def get_enclosure_url(item):
    return item['enclosure'][0]['href']

def get_labels(item):
    #Get the list of labels on an item. 
    #So far we just use one label for each item.
    # Need to be expanded later
    return [m.group(0) for m in [re.search('(?<=label/).*', i) for i in item['categories']] if m]

def generate_save_path(item):
    labels = get_labels(item)
    return config.DOWNLOAD_BASE_FOLDER + labels[0] + '/' + item['origin']['title'] + '/'

def change_items_labels(items, add='', rem=''):
    params = {'i': items}
    if add: params['a'] = add
    if rem: params['r'] = rem
    do_post('edit-tag', data = params)
    
def toggle_labels(items):
    change_items_labels(items, rem=config.DOWNLOAD_LABEL, add=config.ARCHIVE_LABEL)



### Sign in upon module import
### You can comment this out and sign in manually
signin()

