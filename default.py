#!/usr/bin/python
# -*- coding: utf-8 -*-
import resources.lib.common as common
import resources.lib.listmovie as listmovie
import resources.lib.listtv as listtv
import os
import sys
import xbmc
import xbmcaddon
import xbmcplugin

pluginHandle = int(sys.argv[1])

__plugin__ = 'Starz Play'
__authors__ = 'bemerson'
__credits__ = 'moneymaker, slices, zero'
__version__ = '0.0.1'

def modes():
    if sys.argv[2] == '':

        cm = [('Force Movie Database Refresh', 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=movies&sitemode=refresh_db'))]
        common.add_directory('Movies', 'movies', 'list_movie_root', contextmenu=cm)

        cm = [('Force TV Database Refresh', 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=tv&sitemode=refresh_db'))]
        common.add_directory('TV Shows', 'tv', 'list_tv_root', contextmenu=cm)

        xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_PLAYLIST_ORDER)
        xbmcplugin.endOfDirectory(pluginHandle)

    elif common.args.mode == 'movies':
        getattr(listmovie, common.args.sitemode)()
    elif common.args.mode == 'tv':
        getattr(listtv, common.args.sitemode)()
    else:
        print common.args

modes()
sys.modules.clear()