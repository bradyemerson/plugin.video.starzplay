#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import urllib

import xbmcplugin
import xbmc
import xbmcgui
import common
import database_tv as tv_db
import database_common


pluginhandle = common.pluginHandle

# 501-POSTER WRAP 503-MLIST3 504=MLIST2 508-FANARTPOSTER 
confluence_views = [500, 501, 502, 503, 504, 508]

###################### Television

def list_tv_root():
    tv_db.update_tv(False)

    cm_u = sys.argv[0] + '?mode=tv&sitemode=list_tvshows_favor_filtered_export&url=""'
    cm = [('Export Favorites to Library', 'XBMC.RunPlugin(%s)' % cm_u)]
    common.add_directory('Favorites', 'tv', 'list_tvshows_favor_filtered', contextmenu=cm)

    cm_u = sys.argv[0] + '?mode=tv&sitemode=list_tvshows_export&url=""'
    cm = [('Export All to Library', 'XBMC.RunPlugin(%s)' % cm_u)]
    common.add_directory('All Shows', 'tv', 'list_tvshows', contextmenu=cm)

    # common.add_directory('Genres', 'tv', 'list_tvshow_types', 'GENRE')
    #common.add_directory('Years', 'tv', 'list_tvshow_types', 'YEARS')
    #common.add_directory('TV Rating', 'tv', 'list_tvshow_types', 'MPAA')
    common.add_directory('Actors', 'tv', 'list_tvshow_types', 'ACTORS')
    #common.add_directory('Watched', 'tv', 'list_tvshows_watched_filtered')
    xbmcplugin.endOfDirectory(pluginhandle)


def list_tvshow_types(type=False):
    if not type:
        type = common.args.url

    if type == 'GENRE':
        mode = 'list_tvshows_genre_filtered'
        items = tv_db.get_types('genres')
    elif type == 'YEARS':
        mode = 'list_tvshows_years_filtered'
        items = tv_db.get_types('year')
    elif type == 'MPAA':
        mode = 'list_tvshows_mpaa_filtered'
        items = tv_db.get_types('mpaa')
    elif type == 'ACTORS':
        mode = 'list_tvshows_actors_filtered'
        items = tv_db.get_types('actors')

    for item in items:
        common.add_directory(item, 'tv', mode, item)

    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(pluginhandle)


def list_tvshows_genre_filtered():
    list_tvshows(export=False, genrefilter=common.args.url)


def list_tvshows_years_filtered():
    list_tvshows(export=False, yearfilter=common.args.url)


def list_tvshows_mpaa_filtered():
    list_tvshows(export=False, mpaafilter=common.args.url)


def list_tvshows_creators_filtered():
    list_tvshows(export=False, creatorfilter=common.args.url)


def list_tvshows_favor_filtered_export():
    list_tvshows_favor_filtered(export=True)


def list_tvshows_favor_filtered():
    list_tvshows(export=False, favorfilter=True)


def list_tvshows_export():
    list_tvshows(export=True)


def list_tvshows(export=False, mpaafilter=False, genrefilter=False, creatorfilter=False, yearfilter=False,
                 favorfilter=False):
    if export:
        import xbmclibrary

        xbmclibrary.setup_library()

    shows = tv_db.get_series(favorfilter=favorfilter).fetchall()
    total = len(shows)

    for showdata in shows:
        if export:
            xbmclibrary.export_series(showdata)
        else:
            _add_series_item(showdata, total)

    if export:
        common.notification('Export Complete')
        if common.get_setting('updatelibraryafterexport') == 'true':
            xbmclibrary.update_xbmc_library()

    else:
        xbmcplugin.setContent(pluginhandle, 'tvshows')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE)
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        # xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_MPAA_RATING)
        #xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE)
        xbmcplugin.endOfDirectory(pluginhandle)

        viewenable = common.get_setting("viewenable")
        if viewenable == 'true':
            view = int(common.get_setting("showview"))
            xbmc.executebuiltin("Container.SetViewMode(" + str(confluence_views[view]) + ")")


def _add_series_item(data, total=0):
    fanart = database_common.get_thumb(data['content_id'])
    poster = database_common.get_poster(data['content_id'])

    labels = {
        'title': data['title'],
        'tvshowtitle': data['title'],
        'plot': data['plot'],
        'studio': data['studio'],
        'episode': tv_db.get_series_total_episodes(data['content_id']),
        'year': tv_db.get_series_year(data['content_id']),
        'trailer': data['trailer']
    }

    if data['directors']:
        labels['director'] = ' / '.join(data['directors'].split(','))
    if data['genres']:
        labels['genres'] = ' / '.join(data['genres'].split(','))
    if data['actors']:
        labels['cast'] = data['actors'].split(',')

    item = xbmcgui.ListItem(data['title'], iconImage=poster, thumbnailImage=poster)
    item.setInfo(type='Video', infoLabels=labels)
    item.setProperty('fanart_image', fanart)

    contextmenu = []
    if data['favor']:
        cm_u = sys.argv[0] + '?url={0}&mode=tv&sitemode=unfavor_series&title={1}'.format(data['content_id'],
                                                                                         urllib.unquote_plus(
                                                                                             data['title']))
        contextmenu.append((common.localise(39006), 'XBMC.RunPlugin(%s)' % cm_u))
    else:
        cm_u = sys.argv[0] + '?url={0}&mode=tv&sitemode=favor_series&title={1}'.format(data['content_id'],
                                                                                       urllib.unquote_plus(
                                                                                           data['title']))
        contextmenu.append((common.localise(39007), 'XBMC.RunPlugin(%s)' % cm_u))

    if data['trailer']:
        cm_u = sys.argv[0] + '?url={0}&mode=tv&sitemode=play_trailer&title={1}&series_id={2}'.format(
            data['trailer'], data['title'], data['content_id'])
        contextmenu.append(('Play trailer', 'XBMC.RunPlugin(%s)' % cm_u))

    item.addContextMenuItems(contextmenu)

    u = sys.argv[0] + '?url={0}&mode=tv&sitemode=list_tv_seasons'.format(data['content_id'])
    xbmcplugin.addDirectoryItem(pluginhandle, url=u, listitem=item, isFolder=True, totalItems=total)


def list_tv_seasons():
    series_id = common.args.url

    seasons = tv_db.get_seasons(series_id).fetchall()
    total = len(seasons)

    for season in seasons:
        _add_season_item(season, total)

    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.setContent(pluginhandle, 'tvshows')
    xbmcplugin.endOfDirectory(pluginhandle)

    viewenable = common.get_setting("viewenable")
    if viewenable == 'true':
        view = int(common.get_setting("seasonview"))
        xbmc.executebuiltin("Container.SetViewMode(" + str(confluence_views[view]) + ")")


def _add_season_item(data, total=0):
    fanart = database_common.get_thumb(data['series_content_id'])
    poster = database_common.get_poster(data['series_content_id'])

    labels = {
        'title': data['title'],
        'tvshowtitle': data['series_title'],
        'studio': data['studio'],
        'season': data['order_rank'],
        'episode': tv_db.get_season_total_episodes(data['series_content_id']),
        'year': tv_db.get_season_year(data['content_id'])
    }

    if data['directors']:
        labels['director'] = ' / '.join(data['directors'].split(','))
    if data['genres']:
        labels['genres'] = ' / '.join(data['genres'].split(','))
    if data['actors']:
        labels['cast'] = data['actors'].split(',')

    item = xbmcgui.ListItem(data['title'], iconImage=poster, thumbnailImage=poster)
    item.setInfo(type='Video', infoLabels=labels)
    item.setProperty('fanart_image', fanart)

    u = sys.argv[0] + '?url={0}&mode=tv&sitemode=list_episodes'.format(data['content_id'])
    xbmcplugin.addDirectoryItem(pluginhandle, url=u, listitem=item, isFolder=True, totalItems=total)


def list_episodes(export=False):
    season_id = common.args.url

    episodes = tv_db.get_episodes(season_id).fetchall()
    total = len(episodes)

    for episode in episodes:
        _add_episode_item(episode, total)

    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
    xbmcplugin.setContent(pluginhandle, 'Episodes')
    xbmcplugin.endOfDirectory(pluginhandle)

    viewenable = common.get_setting("viewenable")
    if viewenable == 'true':
        view = int(common.get_setting("episodeview"))
        xbmc.executebuiltin("Container.SetViewMode(" + str(confluence_views[view]) + ")")


def _add_episode_item(data, total):
    fanart = database_common.get_thumb(data['content_id'])
    poster = database_common.get_poster(data['series_id'])

    labels = {
        'title': data['title'],
        'sorttitle': data['title_sort'],
        'tvshowtitle': data['series_title'],
        'plot': data['plot'],
        'studio': data['studio'],
        'season': data['season_num'],
        'episode': str(data['order_rank'])[-2:],
        'year': data['year'],
        'duration': data['duration'],
        'playcount': data['playcount']
    }

    if data['mpaa']:
        labels['mpaa'] = 'Rated ' + data['mpaa']
    if data['directors']:
        labels['director'] = ' / '.join(data['directors'].split(','))
    if data['genres']:
        labels['genres'] = ' / '.join(data['genres'].split(','))
    if data['actors']:
        labels['cast'] = data['actors'].split(',')

    item = xbmcgui.ListItem(data['title'], data['mpaa'], iconImage=fanart, thumbnailImage=fanart)
    item.setInfo(type='Video', infoLabels=labels)
    item.setProperty('fanart_image', fanart)

    try:
        if data['is_hd']:
            item.addStreamInfo('video', {'codec': 'h264', 'width': 1280, 'height': 720, 'duration': data['duration']})
        else:
            item.addStreamInfo('video', {'codec': 'h264', 'width': 720, 'height': 400, 'duration': data['duration']})

        if data['audio_type'] == '5.1 Surround':
            item.addStreamInfo('audio', {'codec': 'aac', 'channels': 6})
        else:
            item.addStreamInfo('audio', {'codec': 'aac', 'channels': 2})

        if data['cc_available']:
            item.addStreamInfo('subtitle', {'language': 'en'})

    except:
        pass

    contextmenu = []

    if data['playcount'] > 0:
        cm_u = sys.argv[0] + '?url={0}&mode=tv&sitemode=unwatch_episode'.format(data['content_id'])
        contextmenu.append(('Mark as unwatched', 'XBMC.RunPlugin(%s)' % cm_u))
    else:
        cm_u = sys.argv[0] + '?url={0}&mode=tv&sitemode=watch_episode'.format(data['content_id'])
        contextmenu.append(('Mark as watched', 'XBMC.RunPlugin(%s)' % cm_u))

    item.addContextMenuItems(contextmenu)

    play_url = database_common.get_play_url(data['media_id'])
    u = sys.argv[0] + '?url={0}&mode=tv&sitemode=play_movie&content_id={1}'.format(play_url, data['content_id'])

    xbmcplugin.addDirectoryItem(pluginhandle, url=u, listitem=item, isFolder=False, totalItems=total)


def play_movie():
    url = common.args.url
    content_id = int(common.args.content_id)
    kiosk = 'true'

    item = xbmcgui.ListItem()
    if tv_db.watch_episode(content_id) > 0:
        common.refresh_menu()
        xbmc.executebuiltin("RunPlugin(plugin://plugin.program.chrome.launcher/?url=" + urllib.quote_plus(
            url) + "&mode=showSite&kiosk=" + kiosk + ")")

        # We assume the URL is still valid if it's in our database
        xbmcplugin.setResolvedUrl(common.pluginHandle, True, item)

    else:
        xbmcplugin.setResolvedUrl(common.pluginHandle, False, item)


##########################################
# Context Menu Links
##########################################
def refresh_db():
    tv_db.update_tv(True)


def play_trailer():
    url = common.args.url
    title = common.args.title
    series_id = common.args.series_id
    poster = database_common.get_poster(series_id)

    item = xbmcgui.ListItem(label=title, iconImage=poster, thumbnailImage=poster, path=url)

    player = xbmc.Player()
    player.play(url, item)


def favor_series():
    content_id = common.args.url
    if tv_db.favor_series(content_id) > 0:
        common.notification('Added ' + urllib.unquote_plus(common.args.title) + ' to favorites')
        common.refresh_menu()
    else:
        common.notification('Error adding movie to favorites', isError=True)


def unfavor_series():
    content_id = common.args.url
    if tv_db.unfavor_series(content_id) > 0:
        common.notification('Removed ' + urllib.unquote_plus(common.args.title) + ' from favorites')
        common.refresh_menu()
    else:
        common.notification('Error removing movie from favorites', isError=True)


def watch_episode():
    content_id = common.args.url
    if tv_db.watch_episode(content_id) > 0:
        common.refresh_menu()
    else:
        common.notification('Could not update watch count', isError=True)


def unwatch_episode():
    content_id = common.args.url
    tv_db.unwatch_episode(content_id)
    common.refresh_menu()