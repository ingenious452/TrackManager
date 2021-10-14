import xml.etree.ElementTree as ET
import sqlite3


# Handling database
db_file = './tracks.sqlite'
connection = sqlite3.connect(db_file)
cursor = connection.cursor()

# create table with relation to the track
# track table is the main table
table_sql = '''
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Track;
DROP TABLE IF EXISTS Genre;

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
'''

cursor.executescript(table_sql)


tree = ET.parse('Library.xml')
dict_nodes = tree.findall('./dict/dict/dict')

print('Total {} tracks'.format(len(dict_nodes)))

def lookup(element, key):
    found = False
    for child in element:
        if found:
            return child.text
        elif child.tag == 'key' and child.text == key:
            found = True
    return None



def insert_to_database(track,genre, rating,
                       length,count, album, artist):
    
    print(track, genre, rating, count, length, artist, album)
                   
    cursor.execute( '''INSERT OR IGNORE INTO Artist (name)
                VALUES ( ? )''', (artist, ) )
    cursor.execute( '''SELECT id FROM  Artist WHERE name = ?''', (artist, ) )
    artist_id = cursor.fetchone()[0]  # [(10, )]  list of tuples

    cursor.execute('''INSERT OR IGNORE INTO Album (artist_id, title)
                      VALUES ( ?, ? )''', (artist_id, album))
    cursor.execute('SELECT id FROM  Album WHERE title = ?', (album, ))
    album_id = cursor.fetchone()[0]  # [(10, )]  list of tuples

    cursor.execute('''INSERT OR IGNORE INTO Genre (name)
                      VALUES ( ? )''', (genre, ))
    cursor.execute('SELECT id FROM  Genre WHERE name = ?', (genre, ))
    genre_id = cursor.fetchone()[0]  # [(10, )]  list of tuples

    cursor.execute('''INSERT OR REPLACE INTO 
                      Track (title, rating, count, len, album_id, genre_id)
                      VALUES ( ?, ?, ?, ?, ?, ? )''', 
                      (track,  rating, count, length, album_id, genre_id))
    connection.commit()
   

for dict_node in dict_nodes:
    if lookup(dict_node, 'Track ID') is None:
        continue

    track = lookup(dict_node, 'Name')
    genre = lookup(dict_node, 'Genre')
    rating = lookup(dict_node, 'Rating')
    count = lookup(dict_node, 'Play Count')
    length = lookup(dict_node, 'Total Time')

    artist = lookup(dict_node, 'Artist')
    album = lookup(dict_node, 'Album')

    if (track is None 
        or artist is None 
        or album is None
        or genre is None
        or rating is None
        or count is None
        or length is None):
        continue
    
    insert_to_database(track, genre, rating, count, length, artist, album)
print('Done.')