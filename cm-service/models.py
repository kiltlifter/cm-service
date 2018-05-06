# -*- coding: utf-8 -*-
"""
Module Docstring
"""

from command import gather_rpms, netstat_output, diskspace_output
from format import timestamp, default_hosts
import os

__author__ = "Sean Douglas"
__version__ = "0.1.0"
__license__ = "MIT"

SSH_USERNAME = 'sdouglas'
CFG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cm-service.cfg')


class Hosts:
    cached_hosts = set(default_hosts(CFG_FILE))

    @classmethod
    def update_hosts(cls, hosts):
        cls.cached_hosts.update(hosts)

    @classmethod
    def hosts(cls):
        return list(cls.cached_hosts)


class RPMData(Hosts):
    cached_rpms = {
            "last-update": timestamp(),
        }

    @classmethod
    def update_cached_rpms(cls):
        for host in cls.cached_hosts:
            cls.cached_rpms[host] = gather_rpms(host, username=SSH_USERNAME)
            cls.cached_rpms['last-update'] = timestamp()
        return cls.cached_rpms

    @classmethod
    def rpms(cls, cached=True):
        if cached:
            return cls.cached_rpms
        else:
            return cls.update_cached_rpms()


class NetstatData(Hosts):
    cached_netstat = {
        "last-update": timestamp()
    }

    @classmethod
    def update_cached_netstat(cls):
        for host in cls.cached_hosts:
            cls.cached_netstat[host] = netstat_output(host, username=SSH_USERNAME)
            cls.cached_netstat['last-update'] = timestamp()
        return cls.cached_netstat

    @classmethod
    def netstat(cls, cached=True):
        if cached:
            return cls.cached_netstat
        else:
            return cls.update_cached_netstat()


class DiskspaceData(Hosts):
    cached_diskspace = {
        "last-update": timestamp()
    }

    @classmethod
    def update_cached_diskspace(cls):
        for host in cls.cached_hosts:
            cls.cached_diskspace[host] = diskspace_output(host, username=SSH_USERNAME)
            cls.cached_diskspace['last-update'] = timestamp()
        return cls.cached_diskspace

    @classmethod
    def diskspace(cls, cached=True):
        if cached:
            return cls.cached_diskspace
        else:
            return cls.update_cached_diskspace()

