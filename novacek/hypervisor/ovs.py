#!/usr/bin/env python
#
# vim: set expandtab:ts=4:sw=4
#
# Authors:  Jasper Capel
#           Robert van Leeuwen
#
# Function: openvswitch related checks
#
# This software is released under the terms of the Apache License.
#

import sys
import ConfigParser
import re
import logging
log = logging.getLogger(__name__)


try:
    from easyovs import bridge
except:
    log.critical("checking the ovs needs the easy ovs library")
    log.critical("install easyovs: https://github.com/yeasy/easyOVS")
    sys.exit(1)


### OPENVSWITCH RELATED FUNCTIONS ###

def get_bridge(config='/etc/neutron/plugins/openvswitch/ovs_neutron_plugin.ini'):
    c = ConfigParser.RawConfigParser()
    c.read(config)
    bridge_name = c.get('ovs', 'integration_bridge')

    br = bridge.Bridge(bridge_name)
    br.load_flows()
    return br


def parse_flow_match(data):
    r = re.compile('.*dl_vlan=(?P<vlan_id>[0-9]+).*')
    return r.match(data).groupdict()


def parse_flow_actions(data):
    r = re.compile('.*mod_vlan_vid:(?P<vlan_id>[0-9]+).*')
    return r.match(data).groupdict()

def parse_flow(flow):
    return {'ext': str(parse_flow_match(flow.match)['vlan_id']), 'int': str(parse_flow_actions(flow.actions)['vlan_id'])}


def get_vlan_map():
    br = get_bridge()
    out = []
    for flow in br.get_flows():
        if not 'mod_vlan_vid' in flow.actions or not 'dl_vlan' in flow.match:
            continue
        out.append(parse_flow(flow))

    return out

