Novacek
==============

About
--------------

This is a toolset around OpenStack Nova and Neutron.  
The tool can create overviews in various different ways and email owners of vm's (based on the email in the description field of the tenant)
On hypervisors this tool can also inspect libvirt for running instances and check Openvswitch / vlans.  

Running novacek
--------------
Novacek can run anywhere where the appropriate libraries are installed (see requirements.txt)  
Credentials will be pulled from the environment like other OpenStack tools:  
OS_REGION_NAME  
OS_PASSWORD  
OS_AUTH_URL  
OS_USERNAME  
OS_TENANT_NAME  
As an alternative to environment variables the tool will also look at the neutron.conf and try to use credentials specified there.  

Commandline options:  

| Option             | Description |
| -----------------|-------------|
| -l                  | list instances of the server you are currently logged into |
| -l -p               | also ping the instances |
| -l -H $hypervisor   | list instances on hypervisor $hypervisor |
| -l -Z $zone         | list all instances in zone $zone, ALL will return all instances |
| -f                  | choose formatting of result, noborder or table |
| -c                  | choose which fields to return: Host,Zone,Name,ID,Tenant,IP,VLAN,Flavor,Virsh_ID,PING ... |
| -m $message -H $hypervisor | mail the users of hypervisor X their machines with a $message REQUIRES EMAIL TO BE SET IN DESCRIPTION OF TENANT|

* Example 1: Reset the state off all instances on a hypervisor and hard reboot them:  
for x in $(python novacek.py -c ID -l -f noborder -H $hvname); do nova reset-state --active $x; nova reboot --hard $x; done  

* Example 2: mail all tenants on a hypervisor:  
python novacek.py -m "Things gonna break" -H $hvname



Running test_hypervisor
--------------
test_hypervisor will check libvirt and openvswitch VLAN settings.  
Note that these checks are very environment specific, if you run anything else then neutron/ML2/ovs it will probably not work.  
Feel free to extend these checks.  


Additional requirements
--------------
* The python_libvirt library is needed if you want to check the libvirt status of an instance on a hypervisor  
* To do a check if the vlan's are properly set you need the easyOVS library.  
  This toolset can be found here: https://github.com/yeasy/easyOVS  


Sample output Hypervisor
--------------
|  Host|  Zone | Name      |  ID | Tenant |     IP      |  VLAN  |   Flavor   | Virsh_ID |  PING   |
|------|-------|-----------|-----|--------|-------------|--------|------------|----------|---------|
| hv1  | zone4 | instance1 | XXX | team_a | 10.10.18.4  |  53    |  m1.small  |    -1    | ['DOWN']|  
| hv1  | zone4 | instance2 | XXX | team_b | 10.10.19.4  |  54    |  m1.small  |    1     |  ['UP'] |  
| hv1  | zone4 | instance3 | XXX | team_c | 10.10.11.29 |  52    | m1.medium  |    2     |  ['UP'] |  
| hv1  | zone4 | instance4 | XXX | team_c | 10.10.11.22 |  52    | m1.medium  |    3     |  ['UP'] |  

Contributing
--------------
The tool was specifically build for Spilgames internal setup and is not tested on other setups.  
We are running Openstack Icehouse from RDO on SL6 with Neutron and ML2.  
If you want to extend functionality please do a merge request.  
As long as it does not break anything we are open for changes.  


