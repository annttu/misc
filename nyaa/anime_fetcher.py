#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
from nyaan import Parser as nyaanParser, Item
import os, sys
import ConfigParser
from optparse import OptionParser
import io
from transmission import Transmission, TransmissionError

class Parser(nyaanParser):
    def print_url(self):
        for item in self.by_name():
            print(item.link)

    def get_url(self):
        for item in self.by_name():
            return item.link


def main():
    parser = OptionParser()
    parser.add_option("-c", "--config", dest="configfile", help="config file", default="%s/.anime_fetcher.conf" % os.environ['HOME'])
    parser.add_option("-n", "--name", dest="name", help="Short name of anime to fetch")
    parser.add_option("-a", "--all", dest="all", help="Fetch all configured animes", action="store_true", default=False)
    parser.add_option("-t", "--test", dest="test", help="only fetch, don't write anything", action="store_true", default=False)
    (options, args) = parser.parse_args()
    get_all = False
    name = ""
    if not options.configfile:
        print('Give me config file!')
        sys.exit(1)
    if not os.path.exists(options.configfile):
        print('File %s does not exists' % options.configfile)
    if options.all:
        get_all = True
    elif options.name:
        name = options.name.strip().lower()
    else:
        print("Either --name or --all needed!")
        sys.exit(1)
    try:
        configfile = os.path.abspath(options.configfile)
        f = open(configfile,'r')
        configcont = f.read()
        f.close()
    except IOError as e:
        print('Can\'t open file %s, error %s' % (options.configfile, e))
        sys.exit(1)
    config = ConfigParser.RawConfigParser()
    config.readfp(io.BytesIO(configcont))
    tc = None
    if 'transmission' in config.sections():
        port = None
        host = None
        try:
            port = config.get('transmission', 'port')
        except ConfigParser.NoOptionError:
            pass
        try:
            host = config.get('transmission', 'host')
        except ConfigParser.NoOptionError:
            pass
        tc = Transmission(host=host, port=port)
    if get_all:
        animes = config.sections()
        if 'transmission' in animes:
            animes.pop(animes.index('transmission'))
    else:
        animes = [name]
        if name not in config.sections():
            print("Anime named %s not found from config" % name)
            sys.exit(1)
    for anime in animes:
        seed_ratio = None
        destination = None
        try:
            search_term = config.get(anime,'search')
        except ConfigParser.NoOptionError:
            print('Search for anime %s not given in config!' % anime)
            sys.exit(1)
        try:
            seed_ratio = config.get(anime, 'seed_ratio')
        except ConfigParser.NoOptionError:
            pass
        try:
            destination = config.get(anime, 'destination')
        except ConfigParser.NoOptionError:
            #print('No destination set for %s' % anime)
            pass
        numfile = ''.join(ch for ch in anime if ch.isalnum() or ch in '_-').lower()
        numfile = os.path.join(os.environ['HOME'], '.%s_episode' % numfile)
        try:
            f = open(numfile, 'r')
        except IOError as e:
            if e.errno == 2:
                print('Create file %s and add latest episode number to it' % numfile, file=sys.stderr)
                sys.exit(1)
            else:
                print('Error: %s' % e, file=sys.stderr)
                sys.exit(1)
        num = f.readline()
        f.close()
        try:
            num = int(num)
        except:
            print('File %s does not contain number' % numfile, file=sys.stderr)
            sys.exit(1)
        a = Parser(search_term % {'num' : num})
        a.strict()
        a.deduplicate()
        a.print_url()
        if len(a.objects) > 0 and not options.test:
            f = open(numfile, 'w+')
            num = str(num + 1)
            f.write(num)
            f.close()
            if tc:
                try:
                    tc.add_torrent(a.get_url(), seed_ratio=seed_ratio, destination=destination)
                except TransmissionError as e:
                    print("Cannot add torrent, %s" % str(e))

if __name__ == "__main__":
    main()
