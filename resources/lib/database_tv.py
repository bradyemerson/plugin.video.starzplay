#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
from datetime import date
from sqlite3 import dbapi2 as sqlite

import simplejson as json

import xbmcgui
import common
import connection
import database_common as db_common


def create():
    c = _database.cursor()
    c.execute('''CREATE TABLE series
                (content_id INTEGER PRIMARY KEY,
                 title TEXT,
                 plot TEXT,
                 trailer TEXT,
                 year INTEGER,
                 studio TEXT,
                 directors TEXT,
                 actors TEXT,
                 genres TEXT,
                 popularity INTEGER,
                 favor BOOLEAN DEFAULT 0,
                 in_last_update BOOLEAN DEFAULT 1);''')

    c.execute('''CREATE TABLE season
                (content_id INTEGER PRIMARY KEY,
                 series_content_id INTEGER,
                 order_rank INTEGER,
                 title TEXT,
                 studio TEXT,
                 directors TEXT,
                 actors TEXT,
                 genres TEXT,
                 popularity INTEGER,
                 FOREIGN KEY(series_content_id) REFERENCES series(content_id) ON DELETE CASCADE);''')

    c.execute('''CREATE TABLE episode
                (content_id INTEGER PRIMARY KEY,
                 season_content_id INTEGER,
                 media_id TEXT,
                 order_rank INTEGER,
                 title TEXT,
                 title_sort TEXT,
                 plot TEXT,
                 duration INTEGER,
                 year INTEGER,
                 studio TEXT,
                 mpaa TEXT,
                 directors TEXT,
                 actors TEXT,
                 genres TEXT,
                 popularity INTEGER,
                 added_date timestamp,
                 cc_available BOOLEAN,
                 is_hd BOOLEAN,
                 audio_type TEXT,
                 playcount INTEGER DEFAULT 0,
                 FOREIGN KEY(season_content_id) REFERENCES season(content_id) ON DELETE CASCADE);''')

    _database.commit()
    c.close()


def insert_series(content_id, title=None, plot=None, trailer=None, studio=None, directors=None, actors=None,
                  genres=None, popularity=None):
    c = _database.cursor()

    c.execute('''INSERT OR REPLACE INTO series (
                 content_id,
                 title,
                 plot,
                 trailer,
                 studio,
                 directors,
                 actors,
                 genres,
                 popularity,
                 favor,
                 in_last_update) VALUES (
                 :content_id,
                 :title,
                 :plot,
                 :trailer,
                 :studio,
                 :directors,
                 :actors,
                 :genres,
                 :popularity,
                 (SELECT favor FROM series WHERE content_id = :content_id),
                 :in_last_update)''', {
        'content_id': content_id,
        'title': title,
        'plot': plot,
        'trailer': trailer,
        'studio': studio,
        'directors': directors,
        'actors': actors,
        'genres': genres,
        'popularity': popularity,
        'in_last_update': True
    })
    _database.commit()
    c.close()


def insert_season(content_id, series_content_id, order_rank=None, title=None, studio=None, directors=None,
                  actors=None, genres=None, popularity=None):
    c = _database.cursor()

    c.execute('''INSERT OR REPLACE INTO season (
                 content_id,
                 series_content_id,
                 order_rank,
                 title,
                 studio,
                 directors,
                 actors,
                 genres,
                 popularity) VALUES (
                 :content_id,
                 :series_content_id,
                 :order_rank,
                 :title,
                 :studio,
                 :directors,
                 :actors,
                 :genres,
                 :popularity)''', {
        'content_id': content_id,
        'series_content_id': series_content_id,
        'order_rank': order_rank,
        'title': title,
        'studio': studio,
        'directors': directors,
        'actors': actors,
        'genres': genres,
        'popularity': popularity
    })
    _database.commit()
    c.close()


def insert_episode(content_id, season_content_id, order_rank=None, title=None, title_sort=None, plot=None,
                   duration=None,
                   studio=None, mpaa=None, directors=None, actors=None, genres=None, popularity=None, added_date=None,
                   cc_available=None, is_hd=None, audio_type=None, year=None):
    c = _database.cursor()

    c.execute('''INSERT OR REPLACE INTO episode (
                 content_id,
                 season_content_id,
                 order_rank,
                 title,
                 title_sort,
                 plot,
                 duration,
                 year,
                 studio,
                 mpaa,
                 directors,
                 actors,
                 genres,
                 popularity,
                 added_date,
                 cc_available,
                 is_hd,
                 audio_type,
                 playcount) VALUES (
                 :content_id,
                 :season_content_id,
                 :order_rank,
                 :title,
                 :title_sort,
                 :plot,
                 :duration,
                 :year,
                 :studio,
                 :mpaa,
                 :directors,
                 :actors,
                 :genres,
                 :popularity,
                 :added_date,
                 :cc_available,
                 :is_hd,
                 :audio_type,
                 (SELECT playcount FROM episode WHERE content_id = :content_id))''', {
        'content_id': content_id,
        'season_content_id': season_content_id,
        'order_rank': order_rank,
        'title': title,
        'title_sort': title_sort,
        'plot': plot,
        'duration': duration,
        'year': year,
        'studio': studio,
        'mpaa': mpaa,
        'directors': directors,
        'actors': actors,
        'genres': genres,
        'popularity': popularity,
        'added_date': added_date,
        'cc_available': cc_available,
        'is_hd': is_hd,
        'audio_type': audio_type
    })
    _database.commit()
    c.close()


def lookup_series(content_id):
    c = _database.cursor()
    return c.execute('SELECT DISTINCT * FROM series WHERE content_id = (?)', (content_id,))


def lookup_season(content_id):
    c = _database.cursor()
    return c.execute('SELECT DISTINCT * FROM season WHERE content_id = (?)', (content_id,))


def lookup_episode(content_id):
    c = _database.cursor()
    return c.execute('SELECT DISTINCT * FROM episode WHERE content_id = (?)', (content_id,))


def delete_series(content_id):
    c = _database.cursor()

    c.execute('DELETE FROM series WHERE content_id = (?)', (content_id,))
    c.close()


def watch_episode(content_id):
    # TODO make this actually increment
    c = _database.cursor()
    c.execute("UPDATE episode SET playcount = 1 WHERE content_id = (?)", (content_id,))
    _database.commit()
    c.close()
    return c.rowcount


def unwatch_episode(content_id):
    c = _database.cursor()
    c.execute("UPDATE episode SET playcount=? WHERE content_id = (?)", (0, content_id))
    _database.commit()
    c.close()
    return c.rowcount


def favor_series(content_id):
    c = _database.cursor()
    c.execute("UPDATE series SET favor=? WHERE content_id=?", (True, content_id))
    _database.commit()
    c.close()
    return c.rowcount


def unfavor_series(content_id):
    c = _database.cursor()
    c.execute("UPDATE series SET favor=? WHERE content_id=?", (False, content_id))
    _database.commit()
    c.close()
    return c.rowcount


def get_series(mpaafilter=False, genrefilter=False, yearfilter=False, directorfilter=False,
               watchedfilter=False, favorfilter=False, actorfilter=False, alphafilter=False, studiofilter=False):
    c = _database.cursor()
    if genrefilter:
        genrefilter = '%' + genrefilter + '%'
        return c.execute('SELECT DISTINCT * FROM series WHERE genres LIKE (?)',
                         (genrefilter,))
    elif mpaafilter:
        return c.execute('SELECT DISTINCT * FROM series WHERE mpaa = (?)', (mpaafilter,))
    elif actorfilter:
        actorfilter = '%' + actorfilter + '%'
        return c.execute('SELECT DISTINCT * FROM series WHERE actors LIKE (?)',
                         (actorfilter,))
    elif directorfilter:
        return c.execute('SELECT DISTINCT * FROM series WHERE directors LIKE (?)',
                         (directorfilter,))
    elif studiofilter:
        return c.execute('SELECT DISTINCT * FROM series WHERE studio = (?)', (studiofilter,))
    elif yearfilter:
        return c.execute('SELECT DISTINCT * FROM series WHERE year = (?)', (int(yearfilter),))
    elif watchedfilter:
        return c.execute('SELECT DISTINCT * FROM series WHERE playcount > 0')
    elif favorfilter:
        return c.execute('SELECT DISTINCT * FROM series WHERE favor = 1')
    elif alphafilter:
        return c.execute('SELECT DISTINCT * FROM series WHERE title REGEXP (?)',
                         (alphafilter + '*',))
    else:
        return c.execute('SELECT DISTINCT * FROM series')


def get_series_total_episodes(series_id):
    c = _database.cursor()
    row = c.execute('''SELECT COUNT(e.content_id) AS total_episodes
                  FROM episode AS e
                  JOIN season AS sea ON sea.content_id = e.season_content_id
                  JOIN series AS ser ON ser.content_id = sea.series_content_id
                  WHERE ser.content_id = (?)
                  GROUP BY ser.content_id''', (series_id,)).fetchone()
    c.close()
    if row:
        return row['total_episodes']
    else:
        return 0


def get_series_year(series_id):
    c = _database.cursor()
    row = c.execute('''SELECT e.year FROM episode AS e
                  JOIN season AS sea ON sea.content_id = e.season_content_id
                  JOIN series AS ser ON ser.content_id = sea.series_content_id
                  WHERE ser.content_id = (?)
                  ORDER BY e.year ASC LIMIT 1''', (series_id,)).fetchone()
    c.close()
    if row:
        return row['year']
    else:
        return None


def get_seasons(series_id):
    c = _database.cursor()
    return c.execute('''SELECT DISTINCT sea.*,ser.title AS series_title
                        FROM season AS sea
                        JOIN series AS ser ON ser.content_id = sea.series_content_id
                        WHERE series_content_id = (?)''', (series_id,))


def get_season_total_episodes(season_id):
    c = _database.cursor()
    row = c.execute('''SELECT COUNT(e.content_id) AS total_episodes
                  FROM episode AS e
                  JOIN season AS sea ON sea.content_id = e.season_content_id
                  WHERE sea.content_id = (?)
                  GROUP BY sea.content_id''', (season_id,)).fetchone()
    c.close()
    if row:
        return row['total_episodes']
    else:
        return 0


def get_season_year(season_id):
    c = _database.cursor()
    row = c.execute('''SELECT e.year FROM episode AS e
                  JOIN season AS sea ON sea.content_id = e.season_content_id
                  WHERE sea.content_id = (?)
                  ORDER BY e.year ASC LIMIT 1''', (season_id,)).fetchone()
    c.close()
    if row:
        return row['year']
    else:
        return None


def get_episodes(season_id):
    c = _database.cursor()
    return c.execute('''SELECT DISTINCT e.*, sea.order_rank AS season_num, sea.title AS series_title, sea.content_id AS series_id
                        FROM episode AS e
                        JOIN season AS sea ON sea.content_id = e.season_content_id
                        JOIN series AS ser ON ser.content_id = sea.series_content_id
                        WHERE season_content_id = (?)''', (season_id,))


def get_types(col):
    c = _database.cursor()
    items = c.execute('select distinct %s from series' % col)
    list = []
    for data in items:
        data = data[0]
        if type(data) == type(str()):
            if 'Rated' in data:
                item = data.split('for')[0]
                if item not in list and item <> '' and item <> 0 and item <> 'Inc.' and item <> 'LLC.':
                    list.append(item)
            else:
                data = data.decode('utf-8').encode('utf-8').split(',')
                for item in data:
                    item = item.replace('& ', '').strip()
                    if item not in list and item <> '' and item <> 0 and item <> 'Inc.' and item <> 'LLC.':
                        list.append(item)
        elif data <> 0:
            if data is not None:
                list.append(str(data))
    c.close()
    return list


def update_tv(force=False):
    # Check if we've recently updated and skip
    if not force and not _needs_update():
        return

    dialog = xbmcgui.DialogProgress()
    dialog.create('Refreshing TV Database')
    dialog.update(0, 'Initializing TV Scan')

    json_url = '{0}/metadata-service/play/content/partner/Web_{1}.json?contentType=Series%20with%20Season'.format(db_common.API_DOMAIN, db_common.SERVICE)
    data = connection.get_url(json_url)
    tv_json = json.loads(data)['playContentArray']['playContents']

    # Mark all series as unfound. This will be updated as we go through
    c = _database.cursor()
    c.execute("UPDATE series SET in_last_update = 0")
    _database.commit()
    c.close()

    total = len(tv_json)
    count = 0

    for series in tv_json:
        count += 1
        dialog.update(0, 'Scanned {0} of {1} TV series'.format(count, total))

        actors_list = []
        for actor in series['actors']:
            actors_list.append(actor['fullName'])

        actors = ','.join(actors_list)

        directors_list = []
        for director in series['directors']:
            directors_list.append(director['fullName'])

        directors = ','.join(directors_list)

        trailer = None
        if 'sportURL' in series:
            trailer = series['spotURL']

        insert_series(content_id=series['contentId'], title=series['title'], plot=series['logLine'],
                      trailer=trailer, studio=series['studio'], directors=directors, actors=actors,
                      popularity=series['popularity'])

        # Season Children
        if 'childContent' in series:
            _json_process_seasons(series['childContent'], series['contentId'])

    _set_last_update()

    # Remove unfound movies
    c = _database.cursor()
    c.execute("DELETE FROM series WHERE in_last_update = 0")
    c.close()


def _json_process_seasons(season_data, series_content_id):
    for season in season_data:

        actors_list = []
        for actor in season['actors']:
            actors_list.append(actor['fullName'])

        actors = ','.join(actors_list)

        directors_list = []
        for director in season['directors']:
            directors_list.append(director['fullName'])

        directors = ','.join(directors_list)

        insert_season(content_id=season['contentId'], series_content_id=series_content_id, order_rank=season['order'],
                      title=season['title'], studio=season['studio'], directors=directors, actors=actors,
                      popularity=season['popularity'])

        if 'childContent' in season:
            _json_process_episodes(season['childContent'], season['contentId'])


def _json_process_episodes(episode_data, season_content_id):
    for episode in episode_data:

        duration = int(episode['runtime'] / 60)

        mpaa = episode['mpaaRating']
        if mpaa == 'PG13':
            mpaa = 'PG-13'
        elif 'TV' == mpaa[:2]:
            mpaa = 'TV-' + mpaa[2:]

        actors_list = []
        for actor in episode['actors']:
            actors_list.append(actor['fullName'])

        actors = ','.join(actors_list)

        directors_list = []
        for director in episode['directors']:
            directors_list.append(director['fullName'])

        directors = ','.join(directors_list)

        date_without_time = episode['startDate'][:10]
        added_date = common.parse_date(date_without_time, '%Y-%m-%d')

        insert_episode(content_id=episode['contentId'], season_content_id=season_content_id,
                       order_rank=episode['order'], title=episode['properCaseTitle'], title_sort=episode['titleSort'],
                       plot=episode['logLine'], duration=duration, studio=episode['studio'], mpaa=mpaa,
                       directors=directors, actors=actors, popularity=episode['popularity'], added_date=added_date,
                       cc_available=episode['closedCaption'], is_hd=episode['hd'], audio_type=episode['audioType'],
                       year=episode['releaseYear'])


def _needs_update():
    # Update every 15 days
    if 'last_update' in _database_meta:
        last_update = common.parse_date(_database_meta['last_update'], '%Y-%m-%d')
        return (date.today() - last_update.date()).days > 15

    return True


def _set_last_update():
    _database_meta['last_update'] = date.today().strftime('%Y-%m-%d')
    _write_meta_file()


def _write_meta_file():
    f = open(DB_META_FILE, 'w')
    json.dump(_database_meta, f)
    f.close()


DB_META_FILE = os.path.join(common.__addonprofile__, 'tv.meta')
_database_meta = False
if os.path.exists(DB_META_FILE):
    f = open(DB_META_FILE, 'r')
    _database_meta = json.load(f)
    f.close()
else:
    _database_meta = {}

DB_FILE = os.path.join(common.__addonprofile__, 'tv.db')
if not os.path.exists(DB_FILE):
    _database = sqlite.connect(DB_FILE)
    _database.text_factory = str
    _database.row_factory = sqlite.Row
    create()
else:
    _database = sqlite.connect(DB_FILE)
    _database.text_factory = str
    _database.row_factory = sqlite.Row
