#OFGW Management Plane

The OFGW Management Plane module is responsible for provisioning the management tasks on hardware. It allows for secure control the device by the OFELIA experiment user. It
 also provides a set of tools for the OFGW administrator and the RESTful interface for the [TBAM Agent](https://github.com/fp7-alien/OCF-OFGW/tree/master/TBAM-Agent).

##Architecture
The OFGW Management Plane consists of Command Line Interface for both OFELIA users and OFGW administrator, inventory database, plugins for each hardware type and RESTful interface.

###Command Line Interface

The OFGW Mngt CLI allows on remote control of the devices as well as getting status reports. The access to the specific commands is restricted by the user role: OFGW administrator or OFELIA experiment user. The table below presents OFGW CLI commands.

####Role: OFELIA user
Command  | Description
------------- | -------------
reboot [DEVICE_ID] | Reboot the device
fact-reset | Reset the device and restory the factory settings
show | Show the device configuration
show --ports | Show port status
show --of | Show OpenFlow configuration
show --tables | Show OpenFlow tables dump
show --neighbors | Show device's neighbors

####Role: OFGW administrator
Command  | Description
------------- | -------------
list | List all devices
list --status | List all devices and gets the device status<br />(UP/DOWN/PING time)
fact-reset | Reset the device and restory the factory settings
admin config | Show the OFGW Mngt configuration<br />(inventory/device groups)
admin users | Show OFELIA users and status

###Inventory database
The inventory database contains configuration files that specifies the hardware groups and specific device mangement interface parameters. The patameters are being used by the hardware group plugin to control and force the user commands. The below snippets presents en example configuration files.

<b>groups.yaml</b>
```
groups:
  - name: group1
    required_params:
      - id
      - host
      - hal
    optional_params:
      - login

  - name: group2
    required_params:
      - id
      - host
    optional_params:
      - login
```

<b>inventory.conf</b>
```
[group1]
id=ID1 host=127.0.0.1
id=ID2 host=127.0.0.2

[group2]
id=ID3 host=127.0.0.3
```

###RESTful interface
The RESTful interface allows the OCF to inform on the current device status thru the TBAM Agent. Below the draft RESTful interface specification is presented.

Method | Url | Response | Description
--- | --- | --- | ---
GET | <i>/of-table</i> | json | The OpenFlow table (all devices)
GET | <i>/of-table/{DPID}</i> | json | The OpenFlow table (specific DPID)
GET | <i>/of-table-raw</i> | json |  The OpenFLow table staus in raw POX controller formatting
GET | <i>/port-status</i> | json |  The port status of the device

<b>Example OpenFlow table response</b>
```
{
  "flowstats": [
    {
      "packet_count": 0,
      "hard_timeout": 0,
      "byte_count": 0,
      "duration_sec": 415,
      "actions": [
        {
          "max_len": 0,
          "type": "OFPAT_OUTPUT",
          "port": 2
        }
      ],
      "duration_nsec": 668000000,
      "priority": 1,
      "idle_timeout": 0,
      "cookie": 0,
      "table_id": 0,
      "match": {
        "dl_type": "IP",
        "nw_proto": 6,
        "tp_dst": 80
      }
    },
    {
      "packet_count": 0,
      "hard_timeout": 0,
      "byte_count": 0,
      "duration_sec": 415,
      "actions": [
        {
          "max_len": 0,
          "type": "OFPAT_OUTPUT",
          "port": 2
        }
      ],
      "duration_nsec": 668000000,
      "priority": 1,
      "idle_timeout": 0,
      "cookie": 0,
      "table_id": 0,
      "match": {
        "dl_type": "ARP",
        "nw_src": "10.0.0.3",
        "nw_dst": "10.0.0.4\/32"
      }
    }
  ],
  "dpid": "00-00-00-00-00-03"
}
```

<b>Example port status response</b>
```
{
  "eth4": "up",
  "eth3": "up",
  "eth1": "up",
  "eth0": "down"
}
```


##INSTALLATION

###Python dependencies
* flask
* yaml
* daemon
* texttable

The Python dependencies can be installed by the command:
<br /><i>pip install [name]</i>

###Running
####Command Line Interface
<i>./ofgw_main.py --help</i>

####RESTful service
<i>python ./daemon_ofgw_mngt.py [start|stop|restart]</i>

Default HTTP service port: 5000
