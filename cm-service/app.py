# -*- coding: utf-8 -*-
"""
Module Docstring
"""

from flask import Flask, Blueprint, request
from flask_restplus import Api, Resource, fields, reqparse
import os

from command import gather_rpms, netstat_output, diskspace_output
from format import rpm_search, timestamp, default_hosts, OutputHandler

from models import RPMData, Hosts, NetstatData, DiskspaceData

__author__ = "Sean Douglas"
__version__ = "0.1.0"
__license__ = "MIT"

TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
SSH_USERNAME = 'sdouglas'

app = Flask(__name__, template_folder=TEMPLATE_PATH)
blueprint = Blueprint('api', __name__, url_prefix='/cm-service')
api = Api(blueprint, doc='/api')
app.register_blueprint(blueprint)


host_data = Hosts()
rpm_data = RPMData()
rpm_data.update_cached_rpms()
netstat_data = NetstatData()
netstat_data.update_cached_netstat()
diskspace_data = DiskspaceData()
diskspace_data.update_cached_diskspace()


host_model = api.model('Hosts', {'hosts': fields.List(fields.String(description='hostname'))})
cache_model = api.model('Cache', {'update': fields.Boolean})

basic_parser = reqparse.RequestParser()
basic_parser.add_argument('nocache', type=bool, required=False, location='args')
basic_parser.add_argument(
    'format', type=str, required=False, location='args',
    choices=('csv', 'json', 'html'), help='Invalid format type specified')


@api.route('/hosts')
class Hosts(Resource):
    def get(self):
        """Get a list of target hosts"""
        data = host_data.hosts()
        return data, 200

    @api.expect(host_model)
    def post(self):
        """Add a list of target hostnames"""
        hosts = api.payload.get('hosts')
        host_data.update_hosts(hosts)
        return api.payload, 201


@api.route('/rpm')
class RPM(Resource):
    @api.expect(basic_parser)
    def get(self):
        """Get installed RPMs for an environment"""
        cache = request.args.get('nocache')
        output = request.args.get('format')
        handler = OutputHandler(cache, output, request.url_rule.rule, request.base_url)
        if handler.cache:
            data = rpm_data.rpms(cached=False)
            return handler.formatter(data)
        else:
            data = rpm_data.rpms()
            return handler.formatter(data)


@api.route('/rpm/<path:hostname>')
class RPMHost(Resource):
    @api.expect(basic_parser)
    def get(self, hostname):
        """Search for RPMs installed on given hostname"""
        cache = request.args.get('nocache')
        output = request.args.get('format')
        handler = OutputHandler(cache, output, request.url_rule.rule, request.base_url)
        if handler.cache:
            data = {"last-update": timestamp(), hostname: gather_rpms(hostname, username=SSH_USERNAME)}
            return handler.formatter(data)
        else:
            data = {"last-update": rpm_data.cached_rpms['last-update'], hostname: rpm_data.cached_rpms.get(hostname)}
            return handler.formatter(data)


@api.route('/rpm-search/<path:rpmname>')
@api.param('rpmname', 'RPM name or regex to look for')
class RPMSearch(Resource):
    @api.expect(basic_parser)
    def get(self, rpmname):
        """Search for RPM by name or Regular Expression"""
        cache = request.args.get('nocache')
        output = request.args.get('format')
        handler = OutputHandler(cache, output, request.url_rule.rule, request.base_url)
        if handler.cache:
            data = rpm_search(rpmname, rpm_data.rpms(cached=False))
            data["last-update"] = timestamp()
            return handler.formatter(data)
        else:
            data = rpm_search(rpmname, rpm_data.cached_rpms)
            data["last-update"] = rpm_data.cached_rpms['last-update']
            return handler.formatter(data)


@api.route('/netstat')
class Netstat(Resource):
    @api.expect(basic_parser)
    def get(self):
        """Return Netstat info"""
        cache = request.args.get('nocache')
        output = request.args.get('format')
        handler = OutputHandler(cache, output, request.url_rule.rule, request.base_url)
        if handler.cache:
            return handler.formatter(netstat_data.netstat(cached=False))
        else:
            return handler.formatter(netstat_data.netstat())


@api.route('/netstat/<path:hostname>')
class NetstatHost(Resource):
    @api.expect(basic_parser)
    def get(self, hostname):
        """Search netstat info by hostname"""
        cache = request.args.get('nocache')
        output = request.args.get('format')
        handler = OutputHandler(cache, output, request.url_rule.rule, request.base_url)
        if cache and cache.lower() == 'true':
            return handler.formatter(
                {"last-update": timestamp(), hostname: netstat_output(hostname, username=SSH_USERNAME)})
        else:
            return handler.formatter(
                {"last-update": netstat_data.cached_netstat['last-update'],
                 hostname: netstat_data.cached_netstat.get(hostname)})


@api.route('/diskspace')
class Diskspace(Resource):
    @api.expect(basic_parser)
    def get(self):
        """Return disk space info"""
        cache = request.args.get('nocache')
        output = request.args.get('format')
        handler = OutputHandler(cache, output, request.url_rule.rule, request.base_url)
        if handler.cache:
            return handler.formatter(diskspace_data.update_cached_diskspace())
        else:
            return handler.formatter(diskspace_data.diskspace())


@api.route('/diskspace/<path:hostname>')
class DiskspaceHost(Resource):
    @api.expect(basic_parser)
    def get(self, hostname):
        """List disk space for hostname"""
        cache = request.args.get('nocache')
        output = request.args.get('format')
        handler = OutputHandler(cache, output, request.url_rule.rule, request.base_url)
        if handler.cache:
            return handler.formatter(
                {"last-update": timestamp(), hostname: diskspace_output(hostname, username=SSH_USERNAME)})
        else:
            return handler.formatter(
                {"last-update": diskspace_data.cached_diskspace['last-update'],
                 hostname: diskspace_data.cached_diskspace.get(hostname)})


@api.route('/cache')
class Caches(Resource):
    @api.expect(cache_model)
    @api.doc(responses={202: 'Cache updated', 302: 'Invalid input'})
    def post(self):
        """Updates all caches"""
        if api.payload.get('update'):
            rpm_data.update_cached_rpms()
            netstat_data.update_cached_netstat()
            diskspace_data.update_cached_diskspace()
            return None, 202
        else:
            return None, 302

