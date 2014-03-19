#The TBAM Agent
The TBAM Agent is a daemon running on the OpenFlow Gateway (OFGW) and is responsible for the configuration Management Plane, Control Plane and Data Plane. Regarding the Management plane, TBAM Agent permits not only to manage the configuration of the network devices, but also to retrieve the information of the forwarding plane thanks to pre-defined functionalities exposed by the Management plane. Moreover, the OFGW is in-charge of redirecting the Control traffic to the user controller and handling the data traffic from and to OFELIA islands. Consequently, TBAM Agent provides the configuration also of Control and Data Plane. The architecture of the OFGW is summarized in bottom port of [figure](https://wiki.man.poznan.pl/alien/img_auth.php/a/a4/Work_distribution.png).


###Data Plane: OpenvSwitch

The aim of the Data Plane module is to guarantee the connection between ALIEN and OFELIA. In particular the Data Plane provides the translation between the ALIEN VLANs and the OFELIA VLANs. 

While in the OFELIA islands VLAN tags are used to isolate the traffic among the different slices, in the ALIEN islands the user can freely tag the traffic with one or more VLAN tags (the VLAN tags are passed to the TBAM Agent through the Expedient UI). As a consequence, an additional process (provided by the Data Plane module) is needed to  swap of the ALIEN VLAN id to the OFELIA VLAN id and vice versa. <br>
The re-tagging mechanism is achieved through an [OpenvSwitch](http://openvswitch.org) instance configured by the TBAM Agent. In particular, static flow entries are configured in the OpenvSwitch to achieve correct VLANs tagging and untagging process. <br>

#####Configuration interface
setOvs(VLANs) and remOvs(VLANs) respectively add or remove the flows entry in the OpenvSwitch for the VLANs mapping. The VLANs parameter is a python dict: *{OFELIA-VLAN : ALIEN-VLAN ...}*; for instance *{"10" : "0xffff", "30" : "20"}* means that OFELIA VLAN 10 is set as untagged within ALIEN and OFELIA VLAN 30 is rewritten to the ALIEN VLAN 20. 
<!--
This process of swapping the VLAN needs a priori information on the correct VLAN mapping configurations. The basic idea is to provide through the GUI the choice of the VLANs used in the ALIEN island. Every single ALIEN VLAN ID must be mapped to one OFELIA VLAN ID.
-->

###Control Plane: TCP Proxy
The OFGW acts as TCP Proxy and forwards the control traffic from the devices to the OpenFlow user's controller and vice-versa. The TCP Proxy is implemented as an [iptables](http://www.netfilter.org/projects/iptables/index.html) configuration handled by the TBAM Agent. 

Additionally, the TBAM Agent takes care of the interruption of the connections after the expiration of a time-slot. This functionality is implemented through the iptables's [conntrack](http://www.netfilter.org/projects/conntrack-tools/index.html) module so that only the TCP proxy is reset without affecting the rest of the OFGW's firewall operations.

#####Configuration interface
*setTCPProxy(controller)* and *remTCPProxy(controller)* respectively activate and disable the forwarding of the control traffic to and from the user's controller. The *controller* parameter is a python string: *"ip:port"*; for instance *"192.168.1.1:6633"*.

##INSTALLATION
The communication with the [TBAM Resource Manager](https://github.com/fp7-alien/OCF-TBAM/blob/master/TBAM-RM/README.md#tbam-resource-manager) is obtained with a SecureXMLRPC interface. Currently, the RPC server in the TBAM Agent uses the Clearinghouse certificates that should be generated in order to enable the communication with the Resource Manager (see also [AMsoil installation](https://github.com/motine/AMsoil/wiki/Installation#wiki-gcf-setup) for more information). The TBAM Agent uses three certificates for the SecureXMLRPC authentication; moreover, the references contained in the code must be compliant with your local path. In particular, the parameters of the certificates used in the TBAM Agent are:

Parameter | Reference
------------- | -------------
SERVER_KEY_PATH | it refers to the server key.
SERVER_CERT_PATH |  it refers to the server cert. 
TRUSTED_CERT_PATH | it refers to trusted certificate issued by Clearinghouse.

On the other hand, in order to communicate with the TBAM Agent, the TBAM Resource Manager must use the correct client certificates defined by parameters *CLIENT_KEY_PATH* and *CLIENT_CERT_PATH* within the Resource Manager's code.
Additional information on the generation of the certificates can be found [here](https://github.com/motine/AMsoil/wiki/Installation#wiki-gcf-setup).

The TBAM Agent can be started launching the "src/main.py" with python. 

To connect the Resource Manager to the TBAM Agent, the two variables *OFGW_ADDRESS* and *OFGW_PORT* in the TBAM Resource Manager's "islandrecurcemaneger.py" must be set to the IP address and TCP port of the SecureXMLRPC server of the TBAM Agent. 

By default, the configuration considers that both TBAM Agent and Resource Manager reside on the same machine (*OFGW_ADDRESS = "127.0.0.1"*) and the TCP port used for the communication is 8234 (*OFGW_PORT = 8234*).

##TODO

####Management Plane: MGMT Actions
The interface with the Management Plane module has not been implemented yet. The Management Plane module provides an access to a device for the island administrators and users. It is used to perform some initial configuration of a device (e.g. VLANs, port configuration, etc.) as well as the configuration of the OpenFlow protocol. The TBAM agent leverages the Management Plane module to return island's topology details to the Expedient UI (e.g. datapath_ids, available ports, links, etc.).


###Authentication of the users
The OFGW represents the only entry point for accessing the ALIEN Island’s network resources. Both users and admins use the Management interface exposed through the OFGW to perform custom configurations of the devices. The access should be granted via ssh public key. In this way the authenticated user is able to access the Management module functionalities. An entity that manages and distributes the ssh public keys of the users has not been implemented yet.
