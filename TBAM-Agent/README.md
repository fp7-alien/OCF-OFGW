#The TBAM Agent
The TBAM Agent is a daemon running on the OpenFlow Gateway (OFGW) and is responsible for the configuration Management Plane, Control Plane and Data Plane. OFGW is deployed as a Debian 6 Linux machine (real or virtual) and is configured/controlled by the TBAM Agent daemon. Regarding the Management plane, TBAM Agent permits not only to manage the configuration of the network devices, but also to retrieve the information of the forwarding plane thanks to pre-defined functionalities exposed by the Management plane. Moreover, the OFGW is in-charge of redirecting the Control traffic to the user controller and handling the data traffic from and to OFELIA islands. Consequently, TBAM Agent provides the configuration also of Control and Data Plane. The architecture of the OFGW is summarized in bottom port of [figure](https://wiki.man.poznan.pl/alien/img_auth.php/a/a4/Work_distribution.png).

##INSTALLATION
The communication with the [TBAM Resource Manager](https://github.com/fp7-alien/OCF-TBAM/blob/master/TBAM-RM/README.md#tbam-resource-manager) is obtained with a SecureXMLRPC interface. 
For testing purposes, the RPC server in the TBAM Agent and the TBAM RM use pre-installed certificates. In real deployments, the [ClearingHouse](http://www.eict.de/c-bas) can be used to generate the certificates. The TBAM Agent uses three certificates for the SecureXMLRPC authentication; moreover, the references contained in the code must be compliant with your local path. In particular, the parameters of the certificates used in the TBAM Agent are:

Parameter | Reference
------------- | -------------
SERVER_KEY_PATH | it refers to the server key.
SERVER_CERT_PATH |  it refers to the server cert. 
TRUSTED_CERT_PATH | it refers to trusted certificate issued by Clearinghouse.

On the other hand, in order to communicate with the TBAM Agent, the TBAM Resource Manager must use the correct client certificates defined by parameters *CLIENT_KEY_PATH* and *CLIENT_CERT_PATH* within the [Resource Manager's code](https://github.com/fp7-alien/OCF-TBAM)

The TBAM Agent can be started entering the folder OCF-OFGW/TBAM-Agent (e.g., *cd OCF-OFGW/TBAM-Agent*) and running the "src/main.py" with python (e.g., *python src/main.py*). The TBAM Agent has been tested with Python version 2.7.

To connect the Resource Manager to the TBAM Agent, the two variables *OFGW_ADDRESS* and *OFGW_PORT* in the TBAM Resource Manager's "islandrecurcemaneger.py" must be set to the IP address and TCP port of the SecureXMLRPC server of the TBAM Agent. 

By default, the configuration considers that both TBAM Agent and Resource Manager reside on the same machine (*OFGW_ADDRESS = "127.0.0.1"*) and the TCP port used for the communication is 8234 (*OFGW_PORT = 8234*).

The TBAM-Agent uses the Management Plane module to retrieve network details such as DPIDs of the devices and links. For testing purposes, this connection is disabled by default and the TBAM-Agent is configured to return fake information.  The connection to the Management Plane module can be enabled/disabled by changing the CONN_WITH_MGMT parameter to True/False in the src/main.py. Obviously, the activation of this connection requires the Management Plane to be installed, configured and started (see [OFGW_MGMT](https://github.com/fp7-alien/OCF-OFGW/tree/master/ofgw_mngt))

##User's authentication
On the OFGW, both users/experimenters and administrators can use the Management interface of the devices to perform custom configurations or to retrieve the current status. The access is guaranteed by the local LDAP client which is connected to the central OFELIA LDAP server to allow the users SSH access using the OFELIA credentials. While the island administrator has always access to the OFGW, normal users are allowed to login only during their experiment time-slot. The LDAP client is configured by the TBAM Agent which, in turn, receives the experiments details (e.g. project id, time-slot, etc.) from the TBAM RM. With these details, the TBAM Agent re-configures the 
LDAP client at the beginning of each time-slot so that only the authorized users are enabled to access the OFGW

###LDAP client configuration
To connect the OFGW’s LDAP client to the central OFELIA LDAP server, the following steps are required:
1. DNS bind between LDAP url and its IP address (add the line LDAP_IP_address LDAP_url to
/etc/hosts);
2. Install package ibpam-ldapd (e.g, apt-get install ibpam-ldapd) and follow the procedure on the 
UI to configure the package. When required:
a. Insert the LDAP url (ldap://ldap.ibbt.fp7-ofelia.eu)
b. Set the correct DN (dc=fp7-ofelia,dc=eu)
c. Select not to root management
d. Authorize the modification of nsswitch.conf: check that passwd,group,netgroup are 
selected.
3. Add auth required pam_access.so in /etc/pam.d/common-auth
4. Add session required pam_mkhomedir.so skel=/etc/skel umask=0022 in 
/etc/pam.d/common-session
5. Create file /etc/security/access.conf (e.g., touch /etc/security/access.conf) and add 
this three line: 
+ : ALL : LOCAL 
+ : @proj_<project_UUID>_<project_name> : ALL
EXCEPT root login:ALL EXCEPT LOCAL
After the configuration, the root user is able to login through a SSH connection. Other users can authenticate only if both 
TBAM Agent and TBAM RM are up and running and the users are associated to the current experiment. 

###OFGW Configurations for users authentication

The configuration process to authenticate the users in the OFGW is detailed considering debian 6 as operating system and a [OFELIA](https://github.com/fp7-ofelia/ocf/wiki/Overview) LDAP sever:

1. DNS bind between LDAP url and its ip address (e.g., add LDAP_ip_address LDAP_url in /etc/hosts)
2.	Install package ibpam-ldapd (e.g, apt-get install ibpam-ldapd) and follow the procedure on the UI to configure the package. When required:
	1. Insert the LDAP url
	2. Set the correct DN
	3. Select not to root management
	4. Authorize the modification of *nsswitch.conf*: check that *passwd,group,netgroup* are selected.
3. Add *auth required    pam_access.so* in */etc/pam.d/common-auth*
4. Add *session     required      pam_mkhomedir.so skel=/etc/skel umask=0022* in */etc/pam.d/common-session*
5. Create file /etc/security/access.conf (for e.g., touch /etc/security/access.conf) and add this three line: <br> 

	```
	+ : ALL : LOCAL*
	+ : @proj_<project_UUID>_<project_name> : ALL*
	EXCEPT root login:ALL EXCEPT LOCAL*
	```
After the configuration, the root user is able to login through a SSH connection. Other users can authenticate only if both TBAM Agent and TBAM RM are up and running and the users are associated to the current experiment.
 
###Configuration interfaceThe TBAM Agent receives the LDAP configuration parameters through the following interface:Set/remUserAuth(projectInfo): respectively write or clear the projectInfo in the /etc/access.conf file. The projectInfo containts project_UUID and project_name and allows to query the LDAP server to authenticate only the permitted users.


##Data Plane: OpenvSwitch

The aim of the Data Plane module is to guarantee the connection between ALIEN and OFELIA. In particular the Data Plane provides the translation between the ALIEN VLANs and the OFELIA VLANs. 

While in the OFELIA islands VLAN tags are used to isolate the traffic among the different slices, in the ALIEN islands the user can freely tag the traffic with one or more VLAN tags (the VLAN tags are passed to the TBAM Agent through the Expedient UI). As a consequence, an additional process (provided by the Data Plane module) is needed to  swap of the ALIEN VLAN id to the OFELIA VLAN id and vice versa. <br>
The re-tagging mechanism is achieved through an [OpenvSwitch](http://openvswitch.org) instance configured by the TBAM Agent. In particular, static flow entries are configured in the OpenvSwitch to achieve correct VLANs tagging and untagging process. 

The Data plane requires  OvS version higher than 2.0.0. The installation procedure is as follows: 

```
sudo apt-get install build-essential fakeroot
wget http://openvswitch.org/releases/openvswitch-2.1.2.tar.gz
tar -zvxf openvswitch-2.1.2.tar.gz && cd openvswitch-2.1.2
fakeroot debian/rules binary
cd ../ && dpkg –i openvswitch-common openvswitch-datapath-dkms openvswitch-datapath-source openvswitch-pki openvswitch-switch
```
The initial OvS configuration process requires running the following commands as root:

```
ovs-vsctl add-br switch -- set Bridge switch fail-mode=secure
ovs-ofctl add-flow switch "priority=0, actions=drop"
```
The port configuration considers two ports: one connected to OFELIA (OFELIAPort) and the other to an ALIEN device  (ALIENPort). The port configuration requires these three commands:

```
ovs-vsctl add-port switch ALIENPort -- set Interface ALIENPort ofport_request=2
ovs-ofctl mod-port switch 2 up
ovs-vsctl add-port switch OFELIAPort -- set Interface OFELIAPort ofport_request=3
ovs-ofctl mod-port switch 3 up
```

###Configuration interface
setOvs(VLANs) and remOvs(VLANs) respectively add or remove the flows entry in the OpenvSwitch for the VLANs mapping. The VLANs parameter is a python dict: *{OFELIA-VLAN : ALIEN-VLAN ...}*; for instance *{"10" : "0xffff", "30" : "20"}* means that OFELIA VLAN 10 is set as untagged within ALIEN and OFELIA VLAN 30 is rewritten to the ALIEN VLAN 20. 

##Control Plane: TCP Proxy
The OFGW acts as TCP Proxy and forwards the control traffic from the devices to the OpenFlow user's controller and vice-versa. The TCP Proxy is implemented as an [iptables](http://www.netfilter.org/projects/iptables/index.html) configuration handled by the TBAM Agent. 

Additionally, the TBAM Agent takes care of the interruption of the connections after the expiration of a time-slot. This functionality is implemented through the iptables's [conntrack](http://www.netfilter.org/projects/conntrack-tools/index.html) module so that only the TCP proxy is reset without affecting the rest of the OFGW's firewall operations.

The Control Plane requires the iptables version equal or higher to 1.4.14 and conntrack packages. The installation procedure is the following (root previleges are needed):
- conntrack:
	```	apt-get install conntrack	```
- iptables:
	```
	apt-get autoremove iptables	apt-get install git dh-autoreconf pkg-config 
	git clone git://git.netfilter.org/iptables.git	git checkout -b 1.4.20 remotes/origin/stable-1.4.20	./autogen.sh && ./configure && make	make install	cd /sbin	ln -s /usr/local/sbin/iptables iptables 	sysctl net.ipv4.ip_forward=1	```
###Configuration interface
*setTCPProxy(controller)* and *remTCPProxy(controller)* respectively activate and disable the forwarding of the control traffic to and from the user's controller. The *controller* parameter is a python string: *"ip:port"*; for instance *"192.168.1.1:6633"*.


##Management Plane: MGMT Actions
The [Management Plane module](https://github.com/fp7-alien/OCF-OFGW/tree/master/ofgw_mngt) provides an access to a device for the island administrators and users. It is used to perform some initial configuration of a device (e.g., VLANs, port configuration, etc.) as well as the configuration of the OpenFlow protocol. The TBAM agent leverages the Management Plane module to return island's topology details to the Expedient UI (e.g., datapath_ids, available ports, links, etc.). The communication between TBAM-Agent and the Management Plane module is achieved through RESTful interface.


	