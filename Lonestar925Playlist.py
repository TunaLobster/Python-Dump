import codecs
import csv
import time

import requests
import spotify  # See note

# Writen originally for Python 2.7 and adoption for Python 3.5 was started
# Deprecated as of Jul '16 as libspotify binaries are no longer available and no alternative has been developed
# See https://github.com/mopidy/mopidy-spotify/issues/110 for discussion

userName = ''  # guess
password = ''  # you got this

# Track changes to csv
file = codecs.open('925Playlist.csv', 'r', 'utf8')
oldList = [line.strip() for line in file]
file.close()

get = requests.get('http://www.lonestar925.com/playlist/')
file = codecs.open('925Playlist.csv', 'a', 'utf8')
s = 0
e = 0

if get.status_code is 200:
    text = get.text

    if text.find('a class ="title', s) is -1:
        raise Exception('Playlist webpage empty')

    s = text.find('<ol class="chartList')
    if s != -1:
        s += len('<ol class="chartList')
        while text.find('a class ="title', s) != -1:
            # prase track
            s = text.index('<a class ="title', s)
            s += len('<a class ="title')
            s = text.index('>', s) + 1
            e = text.index('</a>', s)
            track = text[s:e]
            # parse artist
            s = text.index('<a class="subtitle', s)
            s += len('<a class ="subtitle')
            s = text.index('>', s) + 1
            e = text.index('</a>', s)
            artist = text[s:e]
            # output to file
            file.write('"%s","%s"\n' % (artist, track))
    else:
        raise Exception("Could not find chartList.")
else:
    print(get)
    raise Exception("Not a proper response from page text.")

file.close()

# Read in file
file = codecs.open('925Playlist.csv', 'r', 'utf8')
unsortedList = [line.strip() for line in file]

# Remove duplicates
unsortedList = list(set(unsortedList))
unsortedList.sort()
list = unsortedList

# Record added tracks
addTracks = [x for x in list if x not in oldList]

print('%s  Tracks to add: %s' % (time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime()), addTracks))

if not addTracks:
    quit()

addTracksFile = codecs.open('AddTracks.csv', 'w', 'utf8')

for i in addTracks:
    addTracksFile.write("%s\n" % i)

addTracksFile.close()

file.close()

file = codecs.open('925Playlist.csv', 'w', 'utf8')

for i in list:
    file.write("%s\n" % i)

file.close()

# Begin adding new tracks to "Lonestar 92.5 KZPS" Spotify playlist#
# Start session and login
session = spotify.Session()
session.login(userName, password)
time.sleep(5)
state = session.connection.state


def state_check():
    session.process_events()
    time.sleep(1)
    state = session.connection.state


# Lazy way to check session. Better would be using events.
state_check()
state_check()
state_check()
state_check()
state_check()

playlist = session.playlist_container[2]
playlist.load(timeout=10)

# Search for each track in CSV. Could be better by checking popularity of the top 5 results.
with codecs.open('AddTracks.csv', 'rb', 'utf8') as csvfile:
    text = csv.reader(csvfile, escapechar='\\')
    for row in text:
        search_artist = row[0]
        search_track = row[1]

        search = session.search('%s %s' % (search_artist, search_track))

        attempts = 25
        while attempts > 0:
            attempts -= 1
            try:
                search.load(timeout=60)
            except:
                time.sleep(3)
                print(attempts)
                continue

        if attempts is 0:
            print('Timeout error')
        else:
            continue

        try:
            track = search.tracks[0].load(timeout=10)
        except:
            print('Search: ' + str(search))
            track = 0
        finally:
            if track is 0:
                print('No search results!')
            else:
                playlist.add_tracks(track)

        state_check()
        state_check()
        time.sleep(1)
        state_check()
        state_check()
        state_check()

state_check()

session.logout()

csvfile.close()

# Optional line for logging. Helpful for debugging. Current issues are with repeats in the CSV.
# print '%s  Tracks to add: %s'%(time.strftime('%a, %d %b %Y %H:%M:%S', time.localtime()),addTracks)
