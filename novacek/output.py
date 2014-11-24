#!/usr/bin/env python
#
# vim: set expandtab:ts=4:sw=4
#
# Authors:  Jasper Capel
#           Robert van Leeuwen
#
# About: Generates output, email or printing
#
# This software is released under the terms of the Apache License.
#

from prettytable import PrettyTable
import compute
import network
import auth
import hypervisor
import smtplib
from email.mime.text import MIMEText

class Output:
    def __init__(self, session, _columns, hv):
        self.s = session       
        self.c = compute.Compute(session)
        self.n = network.Network(session)
        self._columns = _columns
        self.instances = self.c.get_instances(hv)
        tenants = auth.get_tenants(session)
        self.tenants_dict = dict([(t.id, t.name) for t in tenants])
        self.tenant_email = dict([(t.id, t.description) for t in tenants])
        self.ports_dict = self.n.get_ports()
        self.flavors_dict = self.c.get_flavors()
        self.table = PrettyTable(_columns)


    def create_instance_list(self, is_hv, pingcheck=False, no_pingcheck_tenant_ids=[], sort=None):
        '''Create dictionary of instances running on hypervisor(s) hv'''
        instance_list = {}
        for i in self.instances:
            ips = ';'.join([v[0]['addr'] for k, v in i.addresses.iteritems()])
            vlans = ';'.join([self.ports_dict[v[0]['mac_addr']]['vlan'] for k, v in i.addresses.iteritems()])
            host = i._info['os-extended-server-attributes:hypervisor_hostname']
            zone = i._info['os-extended-availability-zone:availability_zone']
            flavor = self.flavors_dict.get(i.flavor['id'], 'unknown')
            status = i._info['status']
            if is_hv:
                virsh_id = hypervisor.libvirt_qemu.get_virsh_id(i.id)
            else:
                virsh_id = 'NOT_SUPPORTED'
            if pingcheck:
                if i.tenant_id in no_pingcheck_tenant_ids:
                    ping_status = "NOT CHECKED"
                else:
                    ping_status = network.ping(ips)
            else:
                ping_status = "CHECK OFF"
            instance_list[i.id] = { 'ID': i.id, \
                                    'Host': host, \
                                    'Zone': zone, \
                                    'Name': i.name, \
                                    'TID': i.tenant_id, \
                                    'Tenant': self.tenants_dict.get(i.tenant_id, 'ORPHAN'), \
                                    'Status': status, \
                                    'IP': ips, \
                                    'VLAN': vlans, \
                                    'Flavor': flavor, \
                                    'Virsh_ID': virsh_id, \
                                    'PING': ping_status }
        return instance_list


    def print_instance_list(self, is_hv, pingcheck=False, no_pingcheck_tenant_ids=[], sort=None, format='table', columns=None):
        ''' Create prettytable from instance list '''
        instance_list = self.create_instance_list(is_hv, pingcheck=False, no_pingcheck_tenant_ids=[], sort=None)
        self.make_table(instance_list, sort, format)
        if columns:
            print self.table.get_string(fields=columns)
        else:
            print self.table

    def make_table(self, instance_list, sort=None, format='table'):
        for i in instance_list:
            row = []
            for col in self._columns:
                row.append(instance_list[i][col]) 
            self.table.add_row(row)
        self.table.sortby = sort
        if format == 'noborder':
            self.table.border = False
            self.table.header = False
            self.table.right_padding_width = 1
            self.table.left_padding_width = 0

    def mail_tenants(self, is_hv, maintenance, sort=None, format='table', columns=None):
        ''' Sort instances by tenant and create tables we can email'''
        instance_list = self.create_instance_list(is_hv, pingcheck=False, no_pingcheck_tenant_ids=[], sort=None)
        tenant_list = {}
        for i in instance_list:
            if not instance_list[i]['TID'] in tenant_list:
                tenant_list[instance_list[i]['TID']] = {}
            tenant_list[instance_list[i]['TID']][i] = instance_list[i]
        for t in tenant_list:
            self.tenant_email[t]
            self.make_table(tenant_list[t])
            if not columns:
                columns = ['ID', 'Zone', 'Name', 'Tenant', 'Status', 'IP']
            self.email('test@spilcloud.com', maintenance, self.tenant_email[t], self.table.get_string(fields=columns))

    def email(self, sender, maintenance, receiver,node_table):
        message = "Maintenance notification:\n" + maintenance + "\n\nThe following machines are affected:\n" + node_table
                        
        msg = MIMEText(message)
        
        # me == the sender's email address
        # you == the recipient's email address
        msg['Subject'] = 'Maintenance announcement OpenStack'
        msg['From'] = sender
        msg['To'] = receiver

        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        try:
            s = smtplib.SMTP('localhost')
            s.sendmail(sender, [receiver], msg.as_string())
            s.quit()
        except Exception as e:
            print "Error: unable to send email" + str(e)
