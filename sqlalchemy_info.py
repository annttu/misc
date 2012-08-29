#!/usr/bin/env python
# encoding: utf-8

import sys
import json

def usage():
    return "%s file" % sys.argv[0]

def parse_dict(string):
    retval = {}
    string = string.strip('{').strip('}')
    for value in string.split(', \''):
        key, value = value.split('\': ')
        key = key.lstrip('u').strip('\'').rstrip('L')
        value = value.lstrip('u').strip('\'').rstrip('L')
        try:
            value = int(value)
        except:
            pass
        retval[key] = value
    return retval

def parse(lines):
    b = ''
    a = ''
    bstop=False
    for line in lines.splitlines():
        if 'INFO sqlalchemy.engine.base.Engine SELECT ' in line:
            b += line[line.find('INFO sqlalchemy.engine.base.Engine') + 35:]
            b += " "
        elif 'sqlalchemy.engine.base.Engine {' in line:
            a += line[line.find('INFO sqlalchemy.engine.base.Engine') + 35:]
        elif '- INFO -' in line:
            if len(b) > 0 and not bstop:
                bstop = True
            continue
        else:
            if not bstop:
                b += line
                b += " "
    a = parse_dict(a)
    try:
        a['table_1'] = "'%s'" % a['table_1']
    except:
        pass
    #print("%s %% %s" % (b,a))
    b = b.strip() % a
    b += ';'
    #b = b.replace('"', "'")
    b = b.replace('"table"', 'table')
    b = b.split()
    while True:
        try:
            a = b.index('JOIN')
        except ValueError:
            try:
                a = b.index('WHERE')
            except ValueError:
                try:
                    a = b.index('FROM')
                except ValueError:
                    try:
                        a = b.index('AND')
                    except ValueError:
                        break
        b[a] = '\n%s' % b[a]
    b = ' '.join(b)
    d = b.split(',')
    b=''
    a=''
    for i in d:
        a += "%s, " % i
        if len(a) > 70:
            b+='%s\n' % a
            a=''
    return b.rstrip().rstrip(',')

def main(args=[]):
    if len(args) == 0:
        print usage()
    for f in args:
        try:
            fh = open(f)
            lines = fh.read()
            fh.close()
            print parse(lines)
        except IOError:
            print('Cannot read file %s' % f)

if __name__ == '__main__':
    main(sys.argv[1:])