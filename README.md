# deluge-feed-inoreader (DFI)
RSS feed your Deluge server with Innoreader service

## About
This is a python script to feed your favorite torrents via RSS to your Deluge server.

All you need to do is tag the article you want to download on inoreader, schedule this python script to run on desent periods, and DFI will send them to Deluge for you.

Right now it only support torrents from RSS services on [extratorrent.cc](http://extratorrent.cc) and [kat.cr](http://kat.cr).

##Requirements
- Python 2.7
- [Deluge](http://deluge-torrent.org/) server with web plugin
- [Inoreader account](http://www.inoreader.com)
- Any scheduling service like cron (or not!)

##Features
- Supports folder structure based on your folders in Innoreader.
- Optionally can mark seeded torrents and hide unseeded ones. (only via extratorrent for now)

##Setup
1. Clone the repo
```shell
git clone git@github.com:maziara/deluge-feed-inoreader.git
```
2. Copy config.py.sample to config.py
```shell
cp config.py.sample config.py
```
3. Edit and make the necessary changes according to comments
4. Run the script
```shell
python main.py
```
5. Schedule the script to run every hour.

##Contribute
Fork, commit your awesome change, submit a pull request.
