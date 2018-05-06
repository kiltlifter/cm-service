# -*- coding: utf-8 -*-
"""
Module Docstring
"""
from datetime import datetime
from subprocess import Popen, PIPE

__author__ = "Sean Douglas"
__version__ = "0.1.0"
__license__ = "MIT"

class Command(object):
    def __init__(self, hostname, username=None, command=None, identity_key=None, domain=None):
        self.identity_key = identity_key
        self.username = username
        self.hostname = hostname
        self.command = command
        self.domain = domain

    def _execute(self, cmd):
        ssh_connect = [
            "ssh",
            self.hostname + "." + self.domain if self.domain else self.hostname
        ]
        if self.identity_key:
            ssh_connect.insert(1, self.identity_key)
            ssh_connect.insert(1, "-i")
        if self.username:
            ssh_connect.insert(1, self.username)
            ssh_connect.insert(1, "-l")
        ssh_connect = " ".join(ssh_connect) + " \'{}\'".format(cmd)
        s = Popen(ssh_connect, shell=True, stdout=PIPE, stderr=PIPE)
        try:
            stdout = s.stdout.readlines()
            if stdout:
                return stdout
            else:
                return s.stderr.readlines()
        finally:
            s.terminate()

    def run(self, command=None):
        if command:
            return self._execute(command)
        elif self.command:
            return self._execute(self.command)
        else:
            raise CommandNotSpecified(
                msg='Command not specified in constructor or "run" method of {}'.format(self.__class__.__name__)
            )


class GatherException(BaseException):
    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class CommandNotSpecified(GatherException):
    def __init__(self, msg):
        super(CommandNotSpecified, self).__init__(msg)


class SubprocessCommandError(GatherException):
    def __init__(self, msg):
        super(SubprocessCommandError, self).__init__(msg)


class StderrException(GatherException):
    def __init__(self, msg):
        super(StderrException, self).__init__(msg)


class MultipleRpmsFoundError(GatherException):
    def __init__(self, msg):
        super(MultipleRpmsFoundError, self).__init__(msg)


def get_rpm_data(rpm_data):
    # return list(map(lambda a: tuple(a.strip("\n").split("|")), [l.decode("utf-8") for l in rpm_data]))
    data = ((map(lambda a: tuple(a.strip("\n").split("|")), [l.decode("utf-8") for l in rpm_data])))
    names = ['name', 'version', 'release', 'arch', 'install_time', 'vendor', 'url']
    rpms = []
    for rpm in data:
        try:
            d = dict(list((name, value) for name, value in zip(names, rpm)))
            d['install_time'] = datetime.fromtimestamp(int(d['install_time'])).strftime('%m-%d-%Y %H:%M:%S')
            # name = '{name}-{version}-{release}.{arch}'.format(**d)
            rpms.append(d)
        except KeyError:
            pass
    return rpms


def gather_rpms(host, username=None):
    c = Command(hostname=host, username=username)
    data = c.run(
        'rpm --queryformat \"%{NAME}|%{VERSION}|%{RELEASE}|%{ARCH}|%{INSTALLTIME}|%{VENDOR}|%{URL}\\n\" -qa')
    if data:
        return get_rpm_data(data)


def get_netstat_data(netstat_data):
    cols = ['protocol', 'recv-q', 'send-q', 'local_address', 'foreign_address', 'state']
    lines = [b.decode('utf-8').strip('\n') for b in netstat_data]
    lines = [l.split('|') for l in lines]
    return list(dict([(k, v) for k, v in zip(cols, line)]) for line in lines)


def netstat_output(host, username=None):
    c = Command(hostname=host, username=username)
    data = c.run('netstat -tuna | sed -n "3,\$p" | tr -s " " "|"')
    if data:
        return get_netstat_data(data)


def get_diskspace_data(diskspace_data):
    cols = ['filesystem', 'type', 'size', 'used', 'avail', 'use_percent', 'mount']
    lines = [b.decode('utf-8').strip('\n') for b in diskspace_data]
    lines = [l.split('|') for l in lines]
    return list(dict([(k, v) for k, v in zip(cols, line)]) for line in lines)


def diskspace_output(host, username=None):
    c = Command(hostname=host, username=username)
    data = c.run('df -hT | sed -n "3,\$p" | tr -s " " "|"')
    if data:
        return get_diskspace_data(data)
