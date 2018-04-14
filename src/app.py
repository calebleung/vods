# SELECT * FROM vods INNER JOIN played ON played.vod_id = vods.vod_id INNER JOIN games ON played.game_id = games.rowid WHERE games.name='Board Games' ORDER BY vods.created_at DESC

from flask import Flask, request, render_template
from flask_caching import Cache
from flask_restful import Resource, Api

import configparser
import json
import requests
import sqlite3

app = Flask(__name__,
        static_folder = "./www/static",
        template_folder = "./www")
api = Api(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

config = configparser.ConfigParser()
config.read('config')

headers = {
    'Accept': 'application/vnd.twitchtv.v5+json',
    'Client-ID': config['Twitch']['client_id']
}

channelData = json.loads(requests.get('https://api.twitch.tv/kraken/channels/{}'.format(config['Twitch']['channel_id']), headers=headers).text)

channel = {}
channel['url'] = channelData['url']
channel['name'] = channelData['display_name']
channel['logo'] = channelData['logo']

class GamesList(Resource):
    @cache.memoize(50)
    def get(self):
        games = []
        with sqlite3.connect(config['DB']['name']) as conn:
            c = conn.cursor()
            for row in c.execute('SELECT name FROM games WHERE redirect IS NULL ORDER BY name COLLATE NOCASE ASC'):
                games.append(row[0])
        return {'games': games}

class Search(Resource):
    @cache.memoize(50)
    def post(self):
        search = ('%{}%'.format(request.form['data']),)
        games = []
        vods = []
        with sqlite3.connect(config['DB']['name']) as conn:
            c = conn.cursor()
            c.execute('SELECT rowid, name FROM games WHERE name LIKE ? ORDER BY name COLLATE NOCASE ASC', search)
            games = c.fetchall()

            for i, game in enumerate(games):
                for row in c.execute('SELECT :gameIndex, played.vod_id, played.start_at, vods.title, vods.created_at FROM played INNER JOIN vods ON vods.vod_id = played.vod_id WHERE game_id=:gameID ORDER BY played.vod_id ASC', {'gameIndex': str(i), 'gameID': game[0]}):
                    vods.append({'game_index': row[0], 'vod_id': row[1], 'start_at': row[2], 'date': row[4]})
        return {'games': games, 'vods': vods}

api.add_resource(GamesList, '/games')
api.add_resource(Search, '/search')

@app.route('/')
def index():
    return render_template('index.html', channel=channel)

if __name__ == '__main__':
    app.run()