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

def initDB():
    conn = sqlite3.connect(config['DB']['name'])
    c = conn.cursor()

    c.execute('''CREATE TABLE sys
             (total_vods int default 0, newest_created_at text, channel_id text default ''' + config['Twitch']['channel_id'] + ')')
    c.execute('''CREATE TABLE games
             (name text, redirect int)''')
    c.execute('''CREATE TABLE vods
             (vod_id int, title text, desc text, created_at text, animated_preview_url text)''')
    c.execute('''CREATE TABLE played
             (vod_id int, start_at text, game_id text, modified int)''')
    c.execute('INSERT INTO sys DEFAULT VALUES')

    conn.commit()
    conn.close()

    print('Tables created!')

def initJS():
    data = json.loads(requests.get('https://api.twitch.tv/kraken/channels/{}'.format(config['Twitch']['channel_id']), headers=headers).text)

    with open('./www/static/config.js', 'w') as f:
        f.write('channelURL = \'{}\';\n'.format(data['url']))
        f.write('channelName = \'{}\';\n'.format(data['display_name']))
        f.write('channelLogo = \'{}\';\n'.format(data['logo']))

def main():
    initDB()
    initJS()

if __name__ == '__main__':
    main()