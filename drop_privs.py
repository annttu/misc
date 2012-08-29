#!/usr/bin/env python

import os, pwd, grp
from multiprocessing import Process

def drop_privileges(uid_name='nobody', gid_name='nogroup'):
    if os.getuid() != 0:
        # We're not root so, like, whatever dude
        return

    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    # Remove group privileges
    os.setgroups([])

    # Try setting the new uid/gid
    os.setgid(running_gid)
    os.setuid(running_uid)

    # Ensure a very conservative umask
    old_umask = os.umask(077)

def gain_privileges():
    os.setuid(0)
    os.setuid(0)
    os.setgroups(['root'])

def a():
        print('Thread: Hey, I\'m #%s' % os.getuid())
        drop_privileges(uid_name='annttu', gid_name='staff')
        print('Thread: Now I\'m #%s' % os.getuid())

if __name__ == '__main__':
    print('Hey, I\'m #%s' % os.getuid())
    b = Process(target=a)
    b.start()
    b.join()
    print('Now I\'m #%s' % os.getuid())
    