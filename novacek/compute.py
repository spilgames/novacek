#!/usr/bin/env python
#
# vim: set expandtab:ts=4:sw=4
#
# Authors:  Jasper Capel
#           Robert van Leeuwen
#
# Function: OpenStack Compute (Nova) related functions
#
# This software is released under the terms of the Apache License.
#

import sys
import auth

# See if we have gevent for major speedup in fetching instance details
# TODO: find out why this is slower on hypervisor but faster on local machine
try:
    import gevent
    from gevent import monkey
    monkey.patch_socket()
    monkey.patch_ssl()
except:
    pass
    #print 'Gevent not available, the brakes are on!'


### OPENSTACK RELATED FUNCTIONS ###
class Compute:
    def __init__(self, session):
        self.nova = auth.get_novaclient(session)
        
    def get_hypervisor(self, fqdn):
        for hv in self.nova.hypervisors.list():
            if hv.hypervisor_hostname == fqdn:
                return hv
        raise Exception('Could not find hypervisor {0}'.format(fqdn))


    def get_hypervisors_in_zone(self, zone):
        if zone == 'ALL':
            return [x for x in self.nova.hypervisors.list()]
        z = self.nova.availability_zones.find(zone_name=zone)
        if 'gevent' in sys.modules:
            work = [gevent.spawn(self.get_hypervisor, x) for x in z.hosts.keys()]
            gevent.joinall(work)
            return [x.value for x in work]
        else:
            return [self.get_hypervisor(x) for x in z.hosts.keys()]


    def get_flavors(self):
        return dict([(x.id, x.name) for x in self.nova.flavors.list()])


    def get_instances(self, hv):
        if not 'gevent' in sys.modules:
            if isinstance(hv, list):
                instance_list = []
                for h in hv:
                    instance_list+=(self.nova.servers.get(x['id']) for x in self.nova.hypervisors.servers(h.id).servers)
                return instance_list
            else:
                return[self.nova.servers.get(x['id']) for x in self.nova.hypervisors.servers(hv.id).servers]

        work = []
        if isinstance(hv, list):
            for h in hv:
                work.extend([gevent.spawn(self.nova.servers.get, x['id']) for x in self.nova.hypervisors.servers(h.id).servers])
        else:
            work.extend([gevent.spawn(self.nova.servers.get, x['id']) for x in self.nova.hypervisors.servers(hv.id).servers])
        gevent.joinall(work)
        values = [x.value for x in work]
        return values
