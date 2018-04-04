import configparser
import sqlite3

config = configparser.ConfigParser()
config.read('config')

def main():
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

if __name__ == '__main__':
    main()