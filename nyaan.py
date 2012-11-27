#!/usr/bin/env python
# encoding: utf-8

import requests
import re
import string
import logging

logging.basicConfig(level=logging.ERROR)

try:
    from bs4 import BeautifulSoup
except ImportError:
    from BeautifulSoup import BeautifulSoup

from dateutil.parser import parse


description_re = re.compile("(?P<seeders>\d+) seeder\(s\), (?P<leechers>\d+) leecher\(s\), (?P<downloads>\d+) downloads - ((?P<megabytes>\d+(\.\d+)? MiB)|(?P<gigabytes>\d+(\.\d+)? GiB))(?P<trusted> - Trusted)?")

# Multiplers for sorting
RESOLUTION = 1
SEEDERS = 0.3
LEECHERS = 0.3

class Item(object):
    def __init__(self, item):
        self.item = item
        self.log = logging.getLogger('Item')
        self.guid = None
        self.resolution = None
        self.link = None
        self.title = None
        self.category = None
        self.bytes = 0
        self.leechers = None
        self.seeders = None
        self.downloads = None
        self.trusted = False
        self.date = None
        self.episode = None
        self.description = None
        self.points = 0
        if self.parse_item():
            self.parse_descrption()
            self.parse_resolution()
            self.parse_name()
            self.parse_episode()
            self.calc_points()

    def parse_item(self):
        try:
            self.link = self.item.link['href']
            self.title = self.item.title.string
        except Exception as e:
            self.log.error('Multifail %s' % e)
            return
        try:
            self.category = self.item.category.string
        except:
            pass
        try:
            self.description = self.item.description.string
        except:
            pass
        try:
            self.date = parse(self.item.date.string)
        except:
            pass
        return True

    def parse_resolution(self):
        match = re.search('\[(\d+p)\]', self.title)
        if match:
            self.resolution = match.group(1)

    def parse_name(self):
        self.name = re.sub('\s*\[(\w|\s)+\]\s*', ' ',self.title)
        self.name = re.sub('\.\w+$', '',self.name)
        self.name = re.sub('^[^a-zA-Z0-9]+', '',self.name)

    def parse_episode(self):
        match = re.search('- (\d+)(\s+|$)', self.name)
        if match:
            self.episode = match.group(1)

    def valid(self):
        if self.link and self.name:
            return True
        else:
            self.log.error('Unvalid')
            return False

    def parse_descrption(self):
        if type(self.description) == type(u'') or type(self.description) == type(''):
            match = description_re.search(self.description)
            if match != None:
                try:
                    self.bytes = int(float(match.group('megabytes')[:-4]) * 1024 * 1024)
                except:
                    try:
                        self.bytes = int(float(match.group('gigabytes')[:-4]) * 1024 * 1024 * 1024)
                    except Exception as e:
			self.log.exception(e)
                        pass
                self.leechers = match.group('leechers')
                self.seeders = match.group('seeders')
                self.downloads = match.group('downloads')
                try:
                    match.group('trusted').strip()
                    self.trusted = True
                except:
                    pass

    def calc_points(self):
        if self.resolution:
            if self.resolution.endswith('p'):
                try:
                    resol = int(self.resolution[:-1])
                    self.points += resol * RESOLUTION
                except:
                    pass
            if 'x' in self.resolution:
                try:
                    x,y = resol.split('x')
                    self.points += int(y) * RESOLUTION
                except:
                    pass
        if self.seeders:
            try:
                self.points += int(self.seeders) * SEEDERS
            except:
                pass
        if self.leechers:
            try:
                self.points += int(self.leechers) * LEECHERS
            except:
                pass

class Parser(object):
    def __init__(self, search):
        self.log = logging.getLogger('Parser')
        self.objects = []
        self.search = search
        self.feedURL = None
        self.create_feedurl()
        self.parse()

    def create_feedurl(self):
        feedBase = "http://www.nyaa.eu/?page=rss&term="
        self.feedURL = feedBase + '+'.join(self.search.split())

    def parse(self):
        xml = requests.get(self.feedURL)
        ## replaces because soup fails to parse link tags
        soup = BeautifulSoup(xml.text.replace('<link>','<link href="').replace('</link>', '" />'),convertEntities=BeautifulSoup.ALL_ENTITIES)
        for item in soup.findAll('item'):
            try:
                i = Item(item)
                if i.valid():
                    self.objects.append(i)
            except Exception as e:
		self.log.exception(e)

    def present(self):
        print(u"{0:_^60s}|{1:_^6s}|{2:_^6s}|{3:_^13s}|{4:_^10s}|{5:_^45s}".format('Name', 'S', 'L', 'Size', 'Resolution', 'Link'))
        for item in self.by_name():
            if item.resolution:
                resol = item.resolution
            else:
                resol = ''
            print(u"{0:<60s}|{1:>5s} |{2:>5s} | {3:<7.1f} MiB | {4:>8s} | {5:>45s}".format(item.name, item.seeders, item.leechers, float(item.bytes)/1024/1024, resol, item.link))

    def by_episodes(self):
        return sorted(self.objects, key=lambda item: item.episode)

    def by_name(self):
        return sorted(self.objects, key=lambda item: item.name)

    def sorted(self):
        return sorted(self.objects, key=lambda item: item.points)

    def deduplicate(self):
        o = {}
        for item in self.objects:
            if item.name not in o:
                o[item.name] = []
            o[item.name].append(item)
        self.objects = []
        for group in o:
            c = sorted(o[group], key=lambda item: item.points)
            self.objects.append(c[-1])



if __name__ == "__main__":
    import sys
    search = 'Fairy Tail Horrible subs'
    if len(sys.argv) > 1:
        search = ' '.join(sys.argv[1:])
    a = Parser(search)
    a.deduplicate()
    a.present()
