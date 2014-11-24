#!/usr/bin/env python
#
# vim: set expandtab:ts=4:sw=4
#
# Authors:  Jasper Capel
#           Robert van Leeuwen
#
# Function: libvirt related checks
#
# This software is released under the terms of the Apache License.
#

import libvirt
from bs4 import BeautifulSoup


### LIBVIRT RELATED FUNCTIONS ###

def get_libvirt():
    '''Gets information on running VMs from libvirt'''
    l = libvirt.openReadOnly(None)
    out = {}

    for i in l.listDomainsID():
        d = l.lookupByID(i)
        uuid = d.UUIDString()
        soup = BeautifulSoup(d.XMLDesc(0))
        interfaces = [{'dev': x.target['dev'],
                    'mac': x.mac['address'],
                    'alias': x.alias['name'],
                    'bridge': x.source['bridge'].replace('qbr','qvo'),
                    } for x in soup.find_all('interface')]
        out[uuid] = {'interfaces': interfaces,
                    'uuid': uuid,
                    'name': d.name(),
                    'id': d.ID()}
    return out

def get_virsh_id(uuid):
    ''' Connect to libvirt to check see if the instance has a virsh ID '''
    conn = libvirt.openReadOnly(None)
    if conn == None:
        return 'LIBVIRT ERROR'
    try:
        virsh = conn.lookupByUUIDString(uuid)
        return  virsh.ID()
    except:
        return "NOT RUNNING"
