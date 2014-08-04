#The TBAM Agent
The TBAM Agent is a daemon running on the OpenFlow Gateway (OFGW) and is responsible for the configuration Management Plane, Control Plane and Data Plane. Regarding the Management plane, TBAM Agent permits not only to manage the configuration of the network devices, but also to retrieve the information of the forwarding plane thanks to pre-defined functionalities exposed by the Management plane. Moreover, the OFGW is in-charge of redirecting the Control traffic to the user controller and handling the data traffic from and to OFELIA islands. Consequently, TBAM Agent provides the configuration also of Control and Data Plane. The architecture of the OFGW is summarized in bottom port of [figure](https://wiki.man.poznan.pl/alien/img_auth.php/a/a4/Work_distribution.png).


##Data Plane: OpenvSwitch

The aim of the Data Plane module is to guarantee the connection between ALIEN and OFELIA. In particular the Data Plane provides the translation between the ALIEN VLANs and the OFELIA VLANs. 

While in the OFELIA islands VLAN tags are used to isolate the traffic among the different slices, in the ALIEN islands the user can freely tag the traffic with one or more VLAN tags (the VLAN tags are passed to the TBAM Agent through the Expedient UI). As a consequence, an additional process (provided by the Data Plane module) is needed to  swap of the ALIEN VLAN id to the OFELIA VLAN id and vice versa. <br>
The re-tagging mechanism is achieved through an [OpenvSwitch](http://openvswitch.org) instance configured by the TBAM Agent. In particular, static flow entries are configured in the OpenvSwitch to achieve correct VLANs tagging and untagging process. <br>

#####Configuration interface
setOvs(VLANs) and remOvs(VLANs) respectively add or remove the flows entry in the OpenvSwitch for the VLANs mapping. The VLANs parameter is a python dict: *{OFELIA-VLAN : ALIEN-VLAN ...}*; for instance *{"10" : "0xffff", "30" : "20"}* means that OFELIA VLAN 10 is set as untagged within ALIEN and OFELIA VLAN 30 is rewritten to the ALIEN VLAN 20. 
<!--
This process of swapping the VLAN needs a priori information on the correct VLAN mapping configurations. The basic idea is to provide through the GUI the choice of the VLANs used in the ALIEN island. Every single ALIEN VLAN ID must be mapped to one OFELIA VLAN ID.
-->

##Control Plane: TCP Proxy
The OFGW acts as TCP Proxy and forwards the control traffic from the devices to the OpenFlow user's controller and vice-versa. The TCP Proxy is implemented as an [iptables](http://www.netfilter.org/projects/iptables/index.html) configuration handled by the TBAM Agent. 

Additionally, the TBAM Agent takes care of the interruption of the connections after the expiration of a time-slot. This functionality is implemented through the iptables's [conntrack](http://www.netfilter.org/projects/conntrack-tools/index.html) module so that only the TCP proxy is reset without affecting the rest of the OFGW's firewall operations.

#####Configuration interface
*setTCPProxy(controller)* and *remTCPProxy(controller)* respectively activate and disable the forwarding of the control traffic to and from the user's controller. The *controller* parameter is a python string: *"ip:port"*; for instance *"192.168.1.1:6633"*.

<!-- MODIFICATO -->
##Management Plane: MGMT Actions
The [Management Plane module](https://github.com/fp7-alien/OCF-OFGW/tree/master/ofgw_mngt) provides an access to a device for the island administrators and users. It is used to perform some initial configuration of a device (e.g., VLANs, port configuration, etc.) as well as the configuration of the OpenFlow protocol. The TBAM agent leverages the Management Plane module to return island's topology details to the Expedient UI (e.g., datapath_ids, available ports, links, etc.). The communication between TBAM-Agent and the Management Plane module is achieved through RESTful interface.


##Users authentication
The OFGW represents the only entry point for accessing the ALIEN Island’s network resources. Both users and admins use the Management interface exposed through the OFGW to perform custom configurations of the devices. 
The access is guaranteed exploiting the OFELIA LDAP server. The OGFW should be configured to permits the ssh access using the OFELIA credential. The OFGW takes care of associate the OFGW to the ALIEN project that is currently granted. In other words OFGW is informed by the [TBAM-RM](https://github.com/fp7-alien/OCF-TBAM) that a new ALIEN slice should be started or stopped and the TBAM-AGENT configures the OFGW to authorized the access of only the users associated with that particular project. The association between users and project is stored inside the LDAP, so the OFGW at each connection will contact the LDAP server to authorize each user. In this way the authenticated user is able to access the Management module functionalities.

####OFGW Configurations for users authentication
The configuration process to authenticate the users in the OFGW is detailed considering debian 6 as operating system and a [OFELIA](https://github.com/fp7-ofelia/ocf/wiki/Overview) LDAP sever:

1. DNS bind between LDAP url and its ip address (for e.g., add LDAP_ip_address LDAP_url in /etc/hosts)
2. Install package ibpam-ldapd (e.g, apt-get install ibpam-ldapd) and follow the instruction to configure the package. When required:
	1. Insert the LDAP url
	2. Set the correct DN
	3. Select not to root management
	4. Authorize the modification of *nsswitch.conf*: check that *passwd,group,netgroup* are selected.
3. Add *auth required    pam_access.so* in */etc/pam.d/common-auth*
4. Add *session     required      pam_mkhomedir.so skel=/etc/skel umask=0022* in */etc/pam.d/common-session*
5. Create file /etc/security/access.conf (for e.g., touch /etc/security/access.conf) and add this three line: <br> 
*+ : ALL : LOCAL <br>
EXCEPT root login:ALL EXCEPT LOCAL*

After the configuration root user is able to login through ssh. Other users can authenticate only if the ALIEN slice is started and they are associated to the project. Moreover not only the installation process of the TBAM-AGENT but also the communication with the TBAM-RM must be completed.
	

<!--FINE MODIFICATO -->

##INSTALLATION
<!-- MODIFICATO -->
The communication with the [TBAM Resource Manager](https://github.com/fp7-alien/OCF-TBAM/blob/master/TBAM-RM/README.md#tbam-resource-manager) is obtained with a SecureXMLRPC interface. Currently, the RPC server in the TBAM Agent uses fixed pre-installed certificates. In production the certifications should be generated using the [ClearingHouse](http://www.eict.de/c-bas). The TBAM Agent uses three certificates for the SecureXMLRPC authentication; moreover, the references contained in the code must be compliant with your local path. By default the references point to the certs folder, where all the certifications for testing are pre-installed. In particular, the parameters of the certificates used in the TBAM Agent are:
<!--FINE MODIFICATO -->

Parameter | Reference
------------- | -------------
SERVER_KEY_PATH | it refers to the server key.
SERVER_CERT_PATH |  it refers to the server cert. 
TRUSTED_CERT_PATH | it refers to trusted certificate issued by Clearinghouse.

On the other hand, in order to communicate with the TBAM Agent, the TBAM Resource Manager must use the correct client certificates defined by parameters *CLIENT_KEY_PATH* and *CLIENT_CERT_PATH* within the Resource Manager's code. AGGIUNGERE LINK!
<!-- MODIFICATO -->
The TBAM Agent can be started entering the folder OCF-OFGW/TBAM-Agent (e.g., *cd OCF-OFGW/TBAM-Agent*) and launching the "src/main.py" with python (e.g., *python src/main.py*). The TBAM Agent has been tested with 2.7 version.
<!--FINE MODIFICATO -->
To connect the Resource Manager to the TBAM Agent, the two variables *OFGW_ADDRESS* and *OFGW_PORT* in the TBAM Resource Manager's "islandrecurcemaneger.py" must be set to the IP address and TCP port of the SecureXMLRPC server of the TBAM Agent. 

By default, the configuration considers that both TBAM Agent and Resource Manager reside on the same machine (*OFGW_ADDRESS = "127.0.0.1"*) and the TCP port used for the communication is 8234 (*OFGW_PORT = 8234*).

<!-- MODIFICATO -->
As aforementioned the TBAM-Agent uses the Management Plane module to retrive network devices information such as DPIDs and links. For testing purposes, this connection is disable by default and the TBAM-Agent is configured to return fake information.  The connection to the Management Plane module can be enabled/disabled by changing the *CONN_WITH_MGMT* parameter to *True*/*False* in the *src/main.py*. Obviously, the activation of this connection requires the installation and start of the Management Plane.
 
<!--FINE MODIFICATO -->
