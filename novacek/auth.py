#!/usr/bin/env python
#
# vim: set expandtab:ts=4:sw=4
#
# Authors:  Jasper Capel
#           Robert van Leeuwen
#
# Funtion: Handles authentication to various OpenStack API's and
# other authentication based (Keystone) functions
#
# This software is released under the terms of the Apache License.
#


from keystoneclient.v2_0.client import Client as keystonec
from neutronclient.v2_0.client import Client as neutronc
from novaclient.v3.client import Client as novac
import ConfigParser
import os


### AUTH FUNCTIONS ###

def get_os_credentials(filename='/etc/neutron/neutron.conf'):
    '''Attempts to get credentials from an openstack config if it exists, otherwise from env'''
    if os.path.exists(filename):
        c = ConfigParser.RawConfigParser()
        s = 'keystone_authtoken'
        c.read(filename)
        creds = {'username': c.get(s, 'admin_user'),
                'password': c.get(s, 'admin_password'),
                'tenant_name': c.get(s, 'admin_tenant_name'),
                'region_name': c.get(s, 'nova_region_name'),
                'auth_url': '{0}://{1}:{2}/v2.0'.format(c.get(s, 'auth_protocol'),
                                                        c.get(s, 'auth_host'),
                                                        c.get(s, 'auth_port'))}
    else:
        creds = {'username': os.getenv('OS_USERNAME'),
                 'password': os.getenv('OS_PASSWORD'),
                 'tenant_name': os.getenv('OS_TENANT_NAME'),
                 'region_name': os.getenv('OS_REGION_NAME', 'ams1'),
                 'auth_url': os.getenv('OS_AUTH_URL')}

    return creds

def get_keystonesession(credentials=None):
    if not credentials:
        credentials = get_os_credentials()

    from keystoneclient.auth.identity import v2
    from keystoneclient import session
    auth = v2.Password(username=credentials['username'],
                       password=credentials['password'],
                       tenant_name=credentials['tenant_name'],
                       auth_url=credentials['auth_url'])
    return session.Session(auth=auth, verify=False)

def get_keystoneclient(session):
    '''Returns keystoneclient instance'''
    return keystonec(session=session)

def get_neutronclient(session):
    '''Returns neutronclient instance'''
    creds = get_os_credentials()
    return neutronc(username=creds['username'],
                    password=creds['password'],
                    tenant_name=creds['tenant_name'],
                    auth_url=creds['auth_url'])

def get_novaclient(session):
    # Version of novaclient we use doesn't support using existing session
    creds = get_os_credentials()
    return novac(creds['username'], creds['password'], creds['tenant_name'], creds['auth_url'], region_name=creds['region_name'])

def get_tenants(session):
    keystone = get_keystoneclient(session)
    return keystone.tenants.list()

def get_tenant_email(session, tid):
    keystone = get_keystoneclient(session)
    return keystone.tenants.get(tid)

def show_creds():
    credentials = get_os_credentials()
    for cred in credentials:
        print "export OS_" + cred.upper() + "=" + credentials[cred]

