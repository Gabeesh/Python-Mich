# vim: set expandtab tabstop=4 shiftwidth=4 autoindent:
#
# File:   tracks.py
# Mark Addinall - December 2015
# Michigan University Computer Science - Python
#
# Synopsis: Ask Spotify for a download of my-track recorded data
#	        from an XML API service.	
#           Collect all of the XML elements that are TRACKS and
#           populate a relational database with the results.
#
#           

import xml.etree.ElementTree as ET
import sqlite3

conn = sqlite3.connect('trackdb.sqlite')
cur = conn.cursor()

# Make some fresh tables using executescript()
cur.executescript('''
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS Genre;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Track;

CREATE TABLE Artist (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT UNIQUE
);

CREATE TABLE Genre (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT UNIQUE
);

CREATE TABLE Album (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    artist_id  INTEGER,
    title   TEXT UNIQUE
);

CREATE TABLE Track (
    id  INTEGER NOT NULL PRIMARY KEY 
        AUTOINCREMENT UNIQUE,
    title TEXT  UNIQUE,
    album_id  INTEGER,
    genre_id  INTEGER,
    len INTEGER, rating INTEGER, count INTEGER
);
''')


fname = raw_input('Enter file name: ')
if ( len(fname) < 1 ) : fname = 'Library.xml'

# <key>Track ID</key><integer>369</integer>
# <key>Name</key><string>Another One Bites The Dust</string>
# <key>Artist</key><string>Queen</string>


def lookup(d, key):
    found = False
    for child in d:
        if found : return child.text
        if child.tag == 'key' and child.text == key :
            found = True
    return None

stuff = ET.parse(fname)
all = stuff.findall('dict/dict/dict')                       # TRACKS are found three levels deep
print 'Dict count:', len(all)                       

for entry in all:
    if ( lookup(entry, 'Track ID') is None ) : continue     # if the TAG isn't a track, we don't care

    name    = lookup(entry, 'Name')                         # suck the XML values out
    artist  = lookup(entry, 'Artist')
    album   = lookup(entry, 'Album')
    genre   = lookup(entry, 'Genre')
    count   = lookup(entry, 'Play Count')
    rating  = lookup(entry, 'Rating')
    length  = lookup(entry, 'Total Time')

    if name is None or artist is None or genre is None or album is None : 
        continue                                            # for us to make a CLEAN entry into
                                                            # relational database, we NEED all od these 
                                                            # elements to be here.

    print name, artist, genre, album, count, rating, length

    cur.execute('''INSERT OR IGNORE INTO Artist (name) 
        VALUES ( ? )''', ( artist, ) )

    cur.execute('SELECT id FROM Artist WHERE name = ? ', (artist, ))
    artist_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Genre (name) 
        VALUES ( ? )''', ( genre, ) )

    cur.execute('SELECT id FROM Genre WHERE name = ? ', (genre, ))
    genre_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Album (title, artist_id) 
        VALUES ( ?, ? )''', ( album, artist_id ) )
    
    cur.execute('SELECT id FROM Album WHERE title = ? ', (album, ))
    album_id = cur.fetchone()[0]

    cur.execute('''INSERT OR REPLACE INTO Track
        (title, album_id, genre_id, len, rating, count) 
        VALUES ( ?, ?, ?, ?, ?, ? )''', 
        ( name, album_id, genre_id, length, rating, count ) )

    conn.commit()


# test database for response as predicted by examination Rubrick
print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"

for row in cur.execute('''SELECT Track.title, Artist.name, Album.title, Genre.name 
                    FROM Track JOIN Genre JOIN Album JOIN Artist 
                       ON Track.genre_id = Genre.ID and Track.album_id = Album.id 
                         AND Album.artist_id = Artist.id
       ORDER BY Artist.name LIMIT 3'''):
    print str(row[0]), row[1], row[2], row[3]




