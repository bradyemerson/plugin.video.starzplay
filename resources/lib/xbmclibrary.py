#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import sys
import string

import xbmc
import xbmcgui
import resources.lib.common as common
import database_tv as tv_db
import database_common as db_common
from bs4 import BeautifulSoup


pluginhandle = common.pluginHandle

if common.get_setting('libraryfolder') == '0':
    MOVIE_PATH = os.path.join(xbmc.translatePath(common.__addonprofile__), 'Movies')
    TV_SHOWS_PATH = os.path.join(xbmc.translatePath(common.__addonprofile__), 'TV')
else:  # == 1
    if common.get_setting('customlibraryfolder') != '':
        MOVIE_PATH = os.path.join(xbmc.translatePath(common.get_setting('customlibraryfolder')), 'Movies')
        TV_SHOWS_PATH = os.path.join(xbmc.translatePath(common.get_setting('customlibraryfolder')), 'TV')
    else:
        # notify of the missing config...
        pass


def setup_library():
    source_path = os.path.join(xbmc.translatePath('special://profile/'), 'sources.xml')
    dialog = xbmcgui.Dialog()

    # ensure the directories exist
    _create_directory(MOVIE_PATH)
    _create_directory(TV_SHOWS_PATH)

    try:
        file = open(source_path, 'r')
        content = file.read()
        file.close()
    except:
        dialog.ok("Error", "Could not read from sources.xml, does it really exist?")
        file = open(source_path, 'w')
        content = "<sources>\n"
        content += "    <programs>"
        content += "        <default pathversion=\"1\"></default>"
        content += "    </programs>"
        content += "    <video>"
        content += "        <default pathversion=\"1\"></default>"
        content += "    </video>"
        content += "    <music>"
        content += "        <default pathversion=\"1\"></default>"
        content += "    </music>"
        content += "    <pictures>"
        content += "        <default pathversion=\"1\"></default>"
        content += "    </pictures>"
        content += "    <files>"
        content += "        <default pathversion=\"1\"></default>"
        content += "    </files>"
        content += "</sources>"
        file.close()

    soup = BeautifulSoup(content)
    video = soup.find("video")

    added_new_paths = False;

    if len(soup.find_all('name', text=db_common.SERVICE_NAME + ' Movies')) < 1:
        movie_source_tag = soup.new_tag('source')

        movie_name_tag = soup.new_tag('name')
        movie_name_tag.string = db_common.SERVICE_NAME + ' Movies'
        movie_source_tag.insert(0, movie_name_tag)

        movie_path_tag = soup.new_tag('path', pathversion='1')
        movie_path_tag.string = MOVIE_PATH
        movie_source_tag.insert(1, movie_path_tag)

        movie_sharing = soup.new_tag('allowsharing')
        movie_sharing.string = 'true'
        movie_source_tag.insert(2, movie_sharing)

        video.append(movie_source_tag)
        added_new_paths = True

    if len(soup.find_all('name', text=db_common.SERVICE_NAME + ' TV')) < 1:
        tv_source_tag = soup.new_tag('source')

        tvshow_name_tag = soup.new_tag('name')
        tvshow_name_tag.string = db_common.SERVICE_NAME + ' TV'
        tv_source_tag.insert(0, tvshow_name_tag)

        tvshow_path_tag = soup.new_tag('path', pathversion='1')
        tvshow_path_tag.string = TV_SHOWS_PATH
        tv_source_tag.insert(1, tvshow_path_tag)

        tvshow_sharing = soup.new_tag('allowsharing')
        tvshow_sharing.string = 'true'
        tv_source_tag.insert(2, tvshow_sharing)

        video.append(tv_source_tag)
        added_new_paths = True

    file = open(source_path, 'w')
    file.write(str(soup))
    file.close()

    if added_new_paths:
        common.notification('Added ' + db_common.SERVICE_NAME + ' Folder to Library')


def update_xbmc_library():
    xbmc.executebuiltin("update_library(video)")


def export_movie(data, makeNFO=True):

    if data['year']:
        filename = _clean_filename(data['title'] + ' (' + str(data['year']) + ')')
    else:
        filename = _clean_filename(data['title'])

    strm_file = filename + ".strm"
    u = sys.argv[0] + '?url={0}&mode=movies&sitemode=play_movie&content_id={1}'.format(data['url'], data['content_id'])
    _save_file(strm_file, u, MOVIE_PATH)

    if makeNFO:
        nfo_file = filename + ".nfo"
        nfo = '<movie>'
        nfo += '<title>' + data['title'] + '</title>'
        if data['year']:
            nfo += '<year>' + str(data['year']) + '</year>'
        if data['plot']:
            nfo += '<outline>' + data['plot'] + '</outline>'
            nfo += '<plot>' + data['plot'] + '</plot>'
        if data['duration']:
            nfo += '<runtime>' + str(data['duration']) + '</runtime>'  ##runtime in minutes
            nfo += _stream_details(str(int(data['duration']) * 60), data['is_hd'], has_subtitles=data['cc_available'])
        else:
            nfo += _stream_details('', data['is_hd'], has_subtitles=data['cc_available'])
        nfo += '<thumb>' + db_common.get_poster(data['content_id']) + '</thumb>'
        if data['mpaa']:
            nfo += '<mpaa>Rated ' + data['mpaa'] + '</mpaa>'
        if data['studio']:
            nfo += '<studio>' + data['studio'] + '</studio>'
        if data['playcount']:
            nfo += '<playcount>{0}</playcount>'.format(data['playcount'])
        if data['genres']:
            for genre in data['genres'].split(','):
                nfo += '<genre>' + genre + '</genre>'
        if data['directors']:
            nfo += '<director>' + ' / '.join(data['directors'].split(',')) + '</director>'
        if data['actors']:
            for actor in data['actors'].split(','):
                nfo += '<actor>'
                nfo += '<name>' + actor + '</name>'
                nfo += '</actor>'
        nfo += '</movie>'
        _save_file(nfo_file, nfo, MOVIE_PATH)


def export_series(series_list):
    for series in series_list:
        dirname = os.path.join(TV_SHOWS_PATH, series['title'].replace(':', ''))
        _create_directory(dirname)

        seasons = tv_db.get_seasons(series['content_id'])
        for season in seasons:
            _export_season(season, dirname)


def _export_season(seasons, series_dir):
    for season in seasons:
        dirname = os.path.join(series_dir, _clean_filename(season['title']))
        _create_directory(dirname)

        episodes = tv_db.get_episodes(season['content_id'])
        _export_episodes(episodes, dirname)


def _export_episodes(episodes, season_dir, makeNFO=True):
    for data in episodes:
        filename = 'S%sE%s - %s' % (data['season_num'], str(data['order_rank'])[-2:], _clean_filename(data['title']))

        strm_file = filename + ".strm"
        u = sys.argv[0] + '?url={0}&mode=tv&sitemode=play_movie&content_id={1}'.format(data['url'], data['content_id'])
        _save_file(strm_file, u, season_dir)

        if makeNFO:
            nfo_file = filename + ".nfo"
            nfo = '<episodedetails>'
            nfo += '<title>' + data['title'] + '</title>'
            nfo += '<season>' + data['season_num'] + '</season>'
            nfo += '<episode>' + str(data['order_rank'])[-2:] + '</episode>'
            if data['year']:
                nfo += '<year>' + str(data['year']) + '</year>'
            if data['plot']:
                nfo += '<outline>' + data['plot'] + '</outline>'
                nfo += '<plot>' + data['plot'] + '</plot>'
            if data['duration']:
                nfo += '<runtime>' + str(data['duration']) + '</runtime>'  ##runtime in minutes
                nfo += _stream_details(str(int(data['duration']) * 60), data['is_hd'], has_subtitles=data['cc_available'])
            else:
                nfo += _stream_details('', data['is_hd'], has_subtitles=data['cc_available'])
            nfo += '<thumb>' + db_common.get_thumb(data['content_id']) + '</thumb>'
            if data['mpaa']:
                nfo += '<mpaa>Rated ' + data['mpaa'] + '</mpaa>'
            if data['studio']:
                nfo += '<studio>' + data['studio'] + '</studio>'
            if data['playcount']:
                nfo += '<playcount>{0}</playcount>'.format(data['playcount'])
            if data['genres']:
                for genre in data['genres'].split(','):
                    nfo += '<genre>' + genre + '</genre>'
            if data['directors']:
                nfo += '<director>' + ' / '.join(data['directors'].split(',')) + '</director>'
            if data['actors']:
                for actor in data['actors'].split(','):
                    nfo += '<actor>'
                    nfo += '<name>' + actor + '</name>'
                    nfo += '</actor>'
            nfo += '</episodedetails>'
            _save_file(nfo_file, nfo, MOVIE_PATH)


def _save_file(filename, data, dir):
    path = os.path.join(dir, filename)
    file = open(path, 'w')
    file.write(data)
    file.close()


def _create_directory(dir_path):
    dir_path = dir_path.strip()
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def _clean_filename(name):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in name if c in valid_chars)


def _stream_details(duration, is_hd, language='en', has_subtitles=False):
    fileinfo = '<fileinfo>'
    fileinfo += '<streamdetails>'
    fileinfo += '<audio>'
    fileinfo += '<channels>2</channels>'
    fileinfo += '<codec>aac</codec>'
    fileinfo += '</audio>'
    fileinfo += '<video>'
    fileinfo += '<codec>h264</codec>'
    fileinfo += '<durationinseconds>' + duration + '</durationinseconds>'
    if is_hd == True:
        fileinfo += '<aspect>1.778</aspect>'
        fileinfo += '<height>720</height>'
        fileinfo += '<width>1280</width>'
    else:
        fileinfo += '<height>400</height>'
        fileinfo += '<width>720</width>'
    fileinfo += '<language>' + language + '</language>'
    # fileinfo += '<longlanguage>English</longlanguage>'
    fileinfo += '<scantype>Progressive</scantype>'
    fileinfo += '</video>'
    if has_subtitles:
        fileinfo += '<subtitle>'
        fileinfo += '<language>eng</language>'
        fileinfo += '</subtitle>'
    fileinfo += '</streamdetails>'
    fileinfo += '</fileinfo>'
    return fileinfo
