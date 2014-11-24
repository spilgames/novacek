#!/usr/bin/env python
#
# vim: set expandtab:ts=4:sw=4
#
# Authors:  Jasper Capel
#           Robert van Leeuwen
#
# Function: OpenStack network (Neutron) related functions
#
# This software is released under the terms of the Apache License.
#

import subprocess
import auth

### NEUTRON RELATED FUNCTIONS ###

class Network:
    def __init__(self, session):
        self.neutron = auth.get_neutronclient(session)
        self.out = {}

    def get_networks(self):
        for network in self.neutron.list_networks()['networks']:
            self.out[network['id']] = network

        return self.out

    def get_ports(self):
        networks = self.get_networks()
        
        for port in self.neutron.list_ports()['ports']:
            port['vlan'] = str(networks[port['network_id']]['provider:segmentation_id'])
            self.out[port['mac_address']] = port

        return self.out

### GENERAL CHECKS ###
def ping(host):
    ''' Ping hosts and return status'''
    if ";" in host:
        pinglist = host.split(';')
    else:
        pinglist = [host]
    hoststatus = []
    for node in pinglist:
        result = subprocess.call(["ping","-c","1",node],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if result == 0:
             hoststatus.append("UP")
        else:
            hoststatus.append("DOWN")
    return hoststatus


