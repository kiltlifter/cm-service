# -*- coding: utf-8 -*-
"""
Module Docstring
"""
import re
from datetime import datetime
from collections import OrderedDict
from flask import Response, render_template
import hashlib
try:
    import configparser
except ImportError:
    import ConfigParser as configparser


__author__ = "Sean Douglas"
__version__ = "0.1.0"
__license__ = "MIT"


def search_rpm_by_name(name, data):
    rpm = re.compile(name)
    for key, val in data.items():
        if type(val) == list:
            for item in val:
                for v in item.values():
                    if rpm.search(v, re.IGNORECASE):
                        yield key, item


def rpm_search(name, data):
    output = {}
    for hostname, match in search_rpm_by_name(name, data):
        if hostname not in output.keys():
            output[hostname] = []
        output[hostname].append(match)
    return output


def default_hosts(cfg_file):
    with open(cfg_file, 'r') as f:
        config = configparser.RawConfigParser()
        config.read(cfg_file)
        try:
            hosts = config.get('hosts', 'all')
            return hosts.split(',')
        except configparser.NoOptionError:
            return []


def timestamp():
    return str(datetime.isoformat(datetime.now()))


class OutputHandler:
    def __init__(self, cache, output, resource, base_url):
        self.cache = cache
        self.default_outputs = ['csv', 'html', 'json']
        self.output = output
        self.resource = resource
        self.base_url = base_url
        self.set_cache()
        self.set_output()
        self.set_resource_name()

    def set_cache(self):
        if self.cache and self.cache.lower() == 'true':
            self.cache = True
        else:
            self.cache = False

    def set_output(self):
        if self.output and self.output.lower() in self.default_outputs:
            self.output = self.output.lower()
        else:
            self.output = 'json'

    def set_resource_name(self):
        if self.resource:
            try:
                self.resource = self.resource.split('/')[-1]
            except IndexError:
                pass

    def format_json(self, data):
        return data

    def format_csv(self, data):
        output = []
        headers = []
        trailer = []
        for k, v in data.items():
            if type(v) == list:
                for item in v:
                    # u = self.unique(','.join(item.values()))
                    vals = []
                    for field, value in OrderedDict(sorted(item.items(), key=lambda a: a[0])).items():
                        if field.upper() not in headers:
                            headers.append(field.upper())
                        vals.append("\"{}\"".format(value))
                    vals.append("\"{}\"".format(k))
                    output.append(','.join(vals))
            elif type(v) == str and k == 'last-update':
                trailer.append(k)
                trailer.append(v)
        headers.append('HOST')
        output.insert(0, ','.join(headers))
        output.append(','.join(trailer))
        resp = Response('\n'.join(output), mimetype='text/csv', status=200)
        resp.headers['Content-Type'] = "text/csv; charset=utf-8"
        resp.headers['Content-Disposition'] = 'inline; filename="{}.csv"'.format(self.resource)
        return resp

    def format_html(self, data):
        header = list(set(list(v for item in data if type(data[item]) != str for val in data[item] for v in val)))
        t_stamp = data.get('last-update')
        template = render_template('default.html', header=header, t_stamp=t_stamp, content=data, base_url=self.base_url)
        resp = Response(template, mimetype='text/html', status=200)
        resp.headers['Content-Type'] = 'text/html'
        return resp


    def unique(self, string_val):
        val = hashlib.md5(string_val.encode('utf-8'))
        return val.hexdigest()

    def formatter(self, data):
        if self.output == 'csv':
            return self.format_csv(data)
        elif self.output == 'html':
            return self.format_html(data)
        else:
            return self.format_json(data)








