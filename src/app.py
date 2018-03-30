# SELECT * FROM vods INNER JOIN played ON played.vod_id = vods.vod_id INNER JOIN games ON played.game_id = games.rowid WHERE games.name='Board Games' ORDER BY vods.created_at DESC

from flask import Flask, request, render_template
from flask_restful import Resource, Api

import configparser
import sqlite3

app = Flask(__name__,
        static_folder = "./dist/static",
        template_folder = "./dist")
api = Api(app)

config = configparser.ConfigParser()
config.read('config')

class GamesList(Resource):
    def get(self):
        games = []
        with sqlite3.connect(config['DB']['name']) as conn:
            c = conn.cursor()
            for row in c.execute('SELECT name FROM games ORDER BY name COLLATE NOCASE ASC'):
                games.append(row[0])
        return {'games': games}

class Search(Resource):
    def get(self, searchString):
        search = ('%{}%'.format(searchString),)
        games = []
        vods = []
        with sqlite3.connect(config['DB']['name']) as conn:
            c = conn.cursor()
            c.execute('SELECT rowid, name FROM games WHERE name LIKE ? ORDER BY name COLLATE NOCASE ASC', search)
            games = c.fetchall()

            for game in games:
                for row in c.execute('SELECT played.vod_id, played.start_at, vods.title, vods.animated_preview_url FROM played INNER JOIN vods ON vods.vod_id = played.vod_id WHERE game_id=:gameID', {'gameID': game[0]}):
                    vods.append(row)
        return {'games': games, 'vods': vods}

api.add_resource(GamesList, '/games')
api.add_resource(Search, '/search/<string:searchString>')

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)