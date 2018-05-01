import argparse
import configparser
import json
import requests
import sqlite3

parser = argparse.ArgumentParser()
parser.add_argument("--force", type=int, nargs='?', const=-1, default=0, help="Force check all (or the last #[FORCE]) VODs/markers.")

args = parser.parse_args()

config = configparser.ConfigParser()
config.read('config')

headers = {
    'Accept': 'application/vnd.twitchtv.v5+json',
    'Client-ID': config['Twitch']['client_id']
}

conn = sqlite3.connect(config['DB']['name'])
c = conn.cursor()

def getGame(game):
    c.execute('SELECT rowid, redirect FROM games WHERE name=?', game)
    rowid = c.fetchone()

    if rowid is None:
        c.execute('INSERT INTO games VALUES (?,NULL)', game)
        conn.commit()
        return c.lastrowid
    elif rowid[1] is not None:
        return rowid[1]
    return rowid[0]

def insertVOD(data):
    c.execute('SELECT EXISTS(SELECT rowid FROM vods WHERE vod_id=:vodID LIMIT 1)', {'vodID': data[0]})
    rowid = c.fetchone()[0]

    if rowid == 0:
        c.execute('INSERT INTO vods VALUES (?,?,?,?,?)', data)
        conn.commit()
    else:
        print('{} already in database.'.format(data[0]))

def insertPlayed(data):
    c.execute('SELECT EXISTS(SELECT 1 FROM played WHERE vod_id=:vodID and start_at=:startAt LIMIT 1)', {'vodID': data[0], 'startAt': data[1]})
    rowid = c.fetchone()[0]

    if rowid == 0:
        c.execute('INSERT INTO played VALUES (?,?,?,NULL)', data)
        conn.commit()
    else:
        print('{} @ {}s already in database.'.format(data[0], data[1]))

def getNumVODsInDB():
    c.execute('SELECT total_vods FROM sys')
    return c.fetchone()[0]

def updateVODsJSON(vodsInDB, totalVODs):
    data = (totalVODs + vodsInDB, vodsInDB,)
    c.execute('UPDATE sys SET total_vods = ? where total_vods = ?', data)
    conn.commit()

def getVODsJSON(limit, offset):
    return json.loads(requests.get('https://api.twitch.tv/kraken/channels/{}/videos?api_version=5&broadcast_type=archive&limit={}&offset={}'.format(config['Twitch']['channel_id'], limit, offset), headers=headers).text)

def main():
    offset = 0
    totalVODs = 0
    jsonLimit = 100
    allVODData = getVODsJSON(jsonLimit, offset)

    try:
        vodsInDB = getNumVODsInDB()
    except sqlite3.OperationalError:
        print('Could not retrieve total_vods from DB. Does the database exist? Have you run init.py?')
        return

    if args.force == 0:     # Default, just add new VODs
        totalVODs = allVODData['_total'] - vodsInDB
    elif args.force > 0:    # Check the last `args.force` number of VODs. Useful if you're missing a marker from a recent broadcast
        totalVODs = args.force
    elif args.force == -1:  # Check _all_ the VODs
        totalVODs = allVODData['_total']

    videos = allVODData['videos']

    if totalVODs < 100:
        if totalVODs <= 0:
            print('No new VODs to add.')
            return
        allVODData = getVODsJSON(totalVODs, offset)
        videos = allVODData['videos']

    while offset < totalVODs:
        print('{}/{}'.format(offset, totalVODs))
        for video in allVODData['videos']:
            vodID = video['_id'][1:]
            markerData = json.loads(requests.get('https://api.twitch.tv/kraken/videos/{}/markers'.format(vodID), headers=headers).text)

            gameID = getGame((video['game'],))

            vodData = (vodID, video['title'], video['description'], video['created_at'], video['animated_preview_url'],)
            playedData = (vodID, '0', gameID,)

            insertVOD(vodData)
            insertPlayed(playedData)

            #print('Title: {} \nGame: {} ID: {} Created: {}'.format(video['title'], video['game'], video['_id'][1:], video['created_at']))

            try:
                if markerData['markers']['game_changes'] is not None:
                    for marker in markerData['markers']['game_changes']:
                        gameID = getGame((marker['label'],))
                        playedData = (vodID, marker['time'], gameID,)
                        insertPlayed(playedData)
                        #print('Game: {} After: {}s {}'.format(marker['label'], marker['time'], vodID))
            except KeyError:
                print('No additional games found for {}'.format(vodID))
                pass

        offset += len(allVODData['videos'])
        allVODData = getVODsJSON(jsonLimit, offset)

    updateVODsJSON(vodsInDB, totalVODs)

    conn.close()

    print('Database updated!')

if __name__ == '__main__':
    main()