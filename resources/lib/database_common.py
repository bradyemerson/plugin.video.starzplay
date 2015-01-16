#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import urllib
from datetime import datetime
import time

import common


SERVICE = 'Starz'
SERVICE_NAME = 'Starz'
WEB_DOMAIN = 'http://www.starzplay.com'
API_DOMAIN = 'https://playdata.starz.com'
IMAGE_DOMAIN = 'http://imagedata.starz.com'

CACHE_PATH = os.path.join(common.__addonprofile__, 'cache')
if not os.path.exists(CACHE_PATH):
    os.makedirs(CACHE_PATH)


def get_poster(content_id):
    poster_path = os.path.join(CACHE_PATH, 'posters')
    if not os.path.exists(poster_path):
        os.makedirs(poster_path)

    poster_url = "{0}/metadata-service/image/partner/Web_{1}/contentId/{2}/key/web_large_key".format(IMAGE_DOMAIN,
                                                                                                     SERVICE,
                                                                                                     content_id)
    poster_file = os.path.join(poster_path, 'poster_{0}.jpg'.format(content_id))

    if not os.path.exists(poster_file):
        try:
            urllib.urlretrieve(poster_url, poster_file)
        except IOError:
            pass

    return poster_file


def get_thumb(content_id):
    thumb_path = os.path.join(CACHE_PATH, 'thumbs')
    if not os.path.exists(thumb_path):
        os.makedirs(thumb_path)

    thumb_url = "{0}/metadata-service/image/partner/AM_{1}/contentId/{2}/key/am_studio_art_large".format(
        IMAGE_DOMAIN, SERVICE, content_id)
    thumb_file = os.path.join(thumb_path, 'thumb_{0}.jpg'.format(content_id))

    if not os.path.exists(thumb_file):
        try:
            urllib.urlretrieve(thumb_url, thumb_file)
        except IOError:
            pass

    return thumb_file


def get_play_url(media_id):
    return "{0}/PlayMedia?id={1}".format(WEB_DOMAIN, media_id)



