# deluge-feed-inoreader (DFI)
RSS feed your Deluge server with Inoreader service

## About
This is a python script to feed your favorite torrents via RSS to your Deluge server.

All you need to do is tag the article you want to download on inoreader, schedule this python script to run on decent periods, and DFI will send them to Deluge for you.

Right now it only support torrents from RSS services on [extratorrent.cc](http://extratorrent.cc) and [kat.cr](http://kat.cr).

## Requirements
- Python 2.7
- Following dependencies:

 ```shell
 sudo apt-get install python-lxml
 sudo pip install deluge_client werkzeug requests
 ```
- [Deluge](http://deluge-torrent.org/) server with web plugin
- [Inoreader account](http://www.inoreader.com)
- Any scheduling service like cron (or not!)

## Features
- Supports folder structure based on your folders in Innoreader.
- Optionally can mark seeded torrents and hide unseeded ones. (only via extratorrent for now)
- Supports rechecking the unseeded torrents to un-hide them again when they come back alive.
- Removing the finished torrents with customizable exceptions based on tracker.

## Setup
1. Clone the repo

 ```shell
 git clone git@github.com:maziara/deluge-feed-inoreader.git
 ```
2. Make a copy of config.py.sample to config.py

 ```shell
 cp config.py.sample config.py
 ```
3. Edit and make the necessary changes according to the comments
4. Run the script

 ```shell
 python main.py
 ```
 If everything goes right, this will fetch your starred items and add them to deluge. Providing you a summary.
5. Now schedule the script to run every hour (or your preferred intervals).

## Contribute
Fork, commit your awesome change, submit a pull request.
