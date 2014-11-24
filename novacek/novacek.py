#!/usr/bin/env python
#
# vim: set expandtab:ts=4:sw=4
#
# Authors:  Jasper Capel
#           Robert van Leeuwen
#
# About: This is a toolset around OpenStack to easy the daily operations
#
# This software is released under the terms of the Apache License.
#


import socket
import sys
import argparse
import logging
import auth
import compute
import output

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


_columns = ['Host', 'Zone', 'Name', 'ID', 'Tenant', 'Status', 'IP', 'VLAN', 'Flavor', 'Virsh_ID', 'PING']

no_pingcheck_tenant_ids = ['']


### MAIN PROGRAM ###

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-H', '--hypervisor', help='FQDN of hypervisor to operate on')
    group.add_argument('-Z', '--zone',
                       help='Zone to operate on - if neither hypervisor or zone are supplied, operate on local machine. Specify ALL to query all zones')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-l', '--list', help='List all instances running on this hypervisor', action='store_true')
    group.add_argument('-m', '--maintenance', help='Send maintenance mail')
    parser.add_argument('-s', '--sort', help='Sort by colum (use with -l)', choices=_columns)
    parser.add_argument('-p', '--ping', help='Also ping the nodes', action='store_true', default=False)
    parser.add_argument('-f', '--format', help='Output format', choices=['noborder', 'table'], default='table')
    parser.add_argument('-c', '--columns', help='Output columns', nargs='+', choices=_columns)
    args = parser.parse_args()

    if not args.list and not args.maintenance:
        parser.print_usage()
        sys.exit(0)

    s = auth.get_keystonesession()
    c = compute.Compute(s)

    if args.zone:
        is_hv = False
        hvs = c.get_hypervisors_in_zone(args.zone)
    elif args.hypervisor:
        is_hv = False
        hvs = c.get_hypervisor(args.hypervisor)
    else:
        is_hv = True
        hvs = c.get_hypervisor(socket.gethostname())

    if is_hv:
        '''Running on hypervisor, need additional modules'''
        try:
            import hypervisor.libvirt_qemu
            is_hv = True
        except:
            logging.warning("\n *** libvirt-python library missing, running without libvirt checks *** \n")
            is_hv = False   

    o = output.Output(s, _columns, hvs)

    if args.list:
        o.print_instance_list(is_hv, args.ping, no_pingcheck_tenant_ids=no_pingcheck_tenant_ids, sort=args.sort, format=args.format, columns=args.columns)

    if args.maintenance:
        o.mail_tenants(is_hv, args.maintenance, sort=args.sort, format=args.format, columns=args.columns)

if __name__ == '__main__':
    main()
