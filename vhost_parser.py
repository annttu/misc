#!/usr/bin/env python
# encoding: utf-8

# Extremely simple vhost parser
# Feel free to use as you wish
# script comes without any warranty
# Antti 'Annttu' Jaakkola
# 2012


class Vhost(object):
    def __init__(self):
        self.address = ''
        self.port = 80
        self.name = ''
        self.aliases = []
        self.ssl = False
        self.user = 'nobody'
        self.group = 'users'
        self.documentroot = ''

f = open('/tmp/vhost.conf', 'r')
vhost = Vhost()
for line in f.readlines():
	line = line.strip()
	if '<virtualhost ' in line.lower():
	    vhost = Vhost()
	    line = line[13:-1].strip()
	    address, port = line.split(':')
	    vhost.address = address
	    if '>' in port:
	        port = port[:-1]
	    vhost.port = port
	elif 'servername' in line.lower():
	    vhost.name = line[11:].strip()
	elif 'serveralias' in line.lower():
	    vhost.aliases = line[11:].strip().split()
	elif 'sslengine on' in line.lower():
	    vhost.ssl = True
	elif 'documentroot' in line.lower():
	    line = line[13:].strip()
	    vhost.documentroot = line
	elif 'suexecusergroup' in line.lower():
	    line = line[15:].strip()
	    user,group = line.split()
	    vhost.user=user
	    vhost.group = group
	elif '</virtualhost>' in line.lower():
	    print("%s" % vars(vhost))
	    