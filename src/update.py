import configparser
import json
import requests
import sqlite3

config = configparser.ConfigParser()
config.read('config')

headers = {
    'Accept': 'application/vnd.twitchtv.v5+json',
    'Client-ID': config['Twitch']['client_id']
}

conn = sqlite3.connect(config['DB']['name'])
c = conn.cursor()

def getGame(game):
    c.execute('SELECT rowid FROM games WHERE name=?', game)
    rowid = c.fetchone()

    if rowid is None:
        c.execute('INSERT INTO games VALUES (?)', game)
        conn.commit()
        return c.lastrowid
    return rowid[0]

def insertVOD(data):
    c.execute('SELECT EXISTS(SELECT rowid FROM vods WHERE vod_id=:vodID LIMIT 1)', {'vodID': data[0]})
    rowid = c.fetchone()[0]

    if rowid == 0:
        c.execute('INSERT INTO vods VALUES (?,?,?,?,?)', data)
        conn.commit()
    else:
        print('{} was found in the db.'.format(data[0]))

def insertPlayed(data):
    c.execute('SELECT EXISTS(SELECT 1 FROM played WHERE vod_id=:vodID and start_at=:startAt LIMIT 1)', {'vodID': data[0], 'startAt': data[1]})
    rowid = c.fetchone()[0]

    if rowid == 0:
        c.execute('INSERT INTO played VALUES (?,?,?)', data)
        conn.commit()
    else:
        print('{} @ {} was found in the db.'.format(data[0], data[1]))

def main():
    offset = 0
    totalVODs = 0
    vodJSONURL = 'https://api.twitch.tv/kraken/channels/{}/videos?api_version=5&broadcast_type=archive&limit=100'.format(config['Twitch']['channel_id'])
    allVODData = json.loads(requests.get(vodJSONURL, headers=headers).text)

    totalVODs = allVODData['_total']
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

            if markerData['markers']['game_changes'] is not None:
                for marker in markerData['markers']['game_changes']:
                    gameID = getGame((marker['label'],))
                    playedData = (vodID, marker['time'], gameID,)
                    insertPlayed(playedData)
                    #print('Game: {} After: {}s {}'.format(marker['label'], marker['time'], vodID))

        offset += len(allVODData['videos'])
        allVODData = json.loads(requests.get(vodJSONURL + '&offset={}'.format(offset), headers=headers).text)

if __name__ == '__main__':
    main()