#!/usr/bin/env python
#
# vim: set expandtab:ts=4:sw=4
#
# Authors:  Jasper Capel
#           Robert van Leeuwen
#
# This software is released under the terms of the Apache License.
#

import unittest
import novacek.nova as nova
import novacek.hypervisor.ovs as ovs
import novacek.hyperbisor.libvirt_qemu as libvirt_qemu
import novacek.auth as auth
import novacek.network as network

### TEST CASES ###
class TestHypervisor(unittest2.TestCase):
    @classmethod
    def setUpClass(self):
        # Get all the data
        s = auth.get_keystonesession()
        hv = nova.get_hypervisor(s, socket.gethostname())
        self.s = s
        self.nova = auth.get_novaclient(s)
        self.neutron = auth.get_neutronclient(s)
        self.vlan_map = ovs.get_vlan_map()
        self.libvirt_instances = libvirt_qemu.get_libvirt()
        self.os_instances = nova.get_instances(s, hv)
        self.os_networks = network.get_networks(s)
        self.os_ports = network.get_ports(s)
        self.ovs_bridge = ovs.get_bridge()
        self.ovs_ports = self.ovs_bridge.get_ports()

    def test_vm_presence(self):
        '''Tests if all VMs that are running on this hypervisor according to Nova are actually running'''
        for vm in self.os_instances:
            self.assertIn(vm.id, self.libvirt_instances)

    def test_vm_ghosts(self):
        '''Tests if all VMs running on this hypervisor should actually be running here according to Nova'''
        nova_uuids = [vm.id for vm in self.os_instances]
        for vm in self.libvirt_instances.keys():
            self.assertIn(vm, nova_uuids)

    def test_vm_vlans(self):
        '''Tests if all VM virtual interfaces are patched into the correct VLAN'''
        vlan_int_ext = dict([(x['int'], x['ext']) for x in self.vlan_map])
        for k, v in self.libvirt_instances.iteritems():
            for i in v['interfaces']:
                ovs_port_vlan = self.ovs_ports[i['bridge']]['vlan']
                # See if this port has a VLAN tag
                self.assertTrue(ovs_port_vlan, msg='Interface {0} of instance {1} has no VLAN'.format(i['dev'], k))
                # See if OpenStack knows about this port
                self.assertIn(i['mac'], self.os_ports, msg='OpenStack does not know about interface {0} of instance {1}'.format(i['dev'], k))
                if ovs_port_vlan and i['mac'] in self.os_ports:
                    # If this port has a VLAN, check if it's the correct one
                    vlan = vlan_int_ext[ovs_port_vlan]
                    os_port = self.os_ports[i['mac']]
                    self.assertEqual(os_port['vlan'], vlan, msg='Interface {0} of instance {1} should be patched into vlan {2}, but is in VLAN {3}'.format(i['dev'], k, os_port['vlan'], vlan))


sys.argv = [sys.argv[0],]
unittest2.main()
