import configparser
import sqlite3

config = configparser.ConfigParser()
config.read('config')

def main():
    conn = sqlite3.connect(config['DB']['name'])
    c = conn.cursor()

    c.execute('''CREATE TABLE sys
             (total_vods text, newest_created_at text)''')
    c.execute('''CREATE TABLE games
             (name text, redirect int)''')
    c.execute('''CREATE TABLE vods
             (vod_id text, title text, desc text, created_at text, animated_preview_url text)''')
    c.execute('''CREATE TABLE played
             (vod_id text, start_at text, game_id text, modified int)''')

    conn.commit()
    conn.close()

    print('Tables created!')

if __name__ == '__main__':
    main()