#!/usr/bin/env python
# encoding: utf-8

import transmissionrpc

class TransmissionError(Exception):
    pass

class Transmission(object):
    def __init__(self, host="localhost", port=9091):
        self.tc = transmissionrpc.Client(host, port=port)

    def add_torrent(self, url, seed_ratio=None, destination=None):
        """
        Add torrent
        @seed_ratio (float) Set added torrent seed_ratio to given number

        @destination (string) Destination directory for torrent
        """
        try:
            torrent = self.tc.add_uri(url)
        except transmissionrpc.TransmissionError as e:
            raise TransmissionError("Cannot add torrent, error '%s'" % str(e))
        if len(torrent) != 1:
            raise TransmissionError('Cannot add torrent %s' % url)
        torrent_id, torrent = torrent.popitem()

        if destination:
            self.set_destination(torrent_id, destination)
        if seed_ratio:
            self.set_seed_ratio(torrent_id, seed_ratio)
        self.tc.start(torrent_id)

    def set_destination(self, torrent_id, destination):
        self.tc.move(torrent_id, destination)

    def set_seed_ratio(self, torrent_id, ratio):
        ratio = float(ratio)
        self.tc.change(torrent_id, seedRatioMode=1)
        self.tc.change(torrent_id, seedRatioLimit=ratio)

    def _get_torrent(self, torrent_id):
        torrent = self.tc.info(torrent_id)
        if len(torrent) == 1:
            return torrent[torrent_id]
        return

if __name__ == "__main__":
    # tests:
    tc = Transmission()
    tc.add_torrent("http://releases.ubuntu.com/8.10/ubuntu-8.10-desktop-i386.iso.torrent", seed_ratio=10.0)
