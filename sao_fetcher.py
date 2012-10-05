#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
from nyaan import Parser as nyaanParser, Item
import os, sys

class Parser(nyaanParser):
    def print_url(self):
        for item in self.by_name():
            print(item.link)

if __name__ == "__main__":
    numfile = os.path.join(os.environ['HOME'], '.sao_episode')
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
    a = Parser('Sword art online Horrible subs %s 1080p' % num)
    a.deduplicate()
    a.print_url()
    if len(a.objects) > 0:
        f = open(numfile, 'w+')
        num = str(num + 1)
        f.write(num)
        f.close()
