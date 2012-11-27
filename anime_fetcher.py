#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
from nyaan import Parser as nyaanParser, Item
import os, sys
import ConfigParser
from optparse import OptionParser
import io

class Parser(nyaanParser):
    def print_url(self):
        for item in self.by_name():
            print(item.link)


def main():
    parser = OptionParser()
    parser.add_option("-c", "--config", dest="configfile", help="config file")
    parser.add_option("-t", "--test", dest="test", help="only fetch, don't write anything", action="store_true", default=False)
    (options, args) = parser.parse_args()
    if not options.configfile:
        print('Give me config file!')
        sys.exit(1)
    if not os.path.exists(options.configfile):
        print('File %s does not exists' % options.configfile)
    try:
        f = open(options.configfile,'r')
        configcont = f.read()
        f.close()
    except IOError as e:
        print('Can\'t open file %s, error %s' % (options.configfile, e))
        sys.exit(1)
    config = ConfigParser.RawConfigParser()
    config.readfp(io.BytesIO(configcont))
    try:
        anime = config.get('fetcher','name')
    except ConfigParser.NoOptionError:
        print('Anime name not given in config!')
        sys.exit(1)
    try:
        search_term = config.get('fetcher','search')
    except ConfigParser.NoOptionError:
        print('Search not given in config!')
        sys.exit(1)
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
    a.deduplicate()
    a.print_url()
    if len(a.objects) > 0 and not options.test:
        f = open(numfile, 'w+')
        num = str(num + 1)
        f.write(num)
        f.close()

if __name__ == "__main__":
    main()
