# Channel-based VOD search

A Python app to catalog and search Twitch VODs.

## Why

Twitch search doesn't return all games played in the same VOD. That is, a six hour VOD with multiple games played will only be in the search results for the first game played. ([Example of missing VODs](https://gfycat.com/CrispGlumCaiman))

## How

Twitch provides an API endpoint which lists when a game is switched to and what the new game is. We push this info into a database and can return it at will. Hooray!

(Unfortunately, there's no endpoint returning stream title changes, so we're omitting titles as they may lead to confusion.)

## Installation

1. `pip install -r requirements.txt`
2. Make a copy of `config.example` and fill in your desired `channel_id` and `client_id`. 
2. `python init.py`
3. `python update.py`
4. `FLASK_APP=app.py flask run`

\* Consider adding a cron to run update.py to add new VODs to the db.

## Usage

* Swiping left/right & arrow keys navigate between pages
* `/` focuses the search bar
* `Esc` clears (and focuses) the search bar
* Search uses `LIKE %[Query]%`

## Example

![Demo Animation](https://thumbs.gfycat.com/GlumElatedDevilfish-size_restricted.gif)

[Demo](https://vods.zx3.org/)