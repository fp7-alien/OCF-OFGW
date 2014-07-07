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
```yaml
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

<span style="background-color: #FFFF00">TODO: Add the description of the configuration files structure.</span>

###RESTful interface
The RESTful interface allows the OCF to inform on the current device status thru the TBAM Agent. Below the draft RESTful interface specification is presented.

Method | Url | Response | Description
--- | --- | --- | ---
GET | <i>/api/help</i> | json | Available REST methods
GET | <i>/of-table</i> | json | OpenFlow table (all devices)
GET | <i>/of-table/{DPID}</i> | json | OpenFlow table (specific DPID)
GET | <i>/of-table-raw</i> | json |   OpenFLow table staus in raw POX controller formatting
GET | <i>/hosts</i> | json |  List of devices under OCF control
GET | <i>/port-status/id/{ID}</i> | json |  Device's port status
GET | <i>/neighbors/id/{ID}</i> | json |  Device's neighbors

<b>Example OpenFlow table response</b>
```json
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
```json
{
  "eth4": "up",
  "eth3": "up",
  "eth1": "up",
  "eth0": "down"
}
```


##INSTALLATION

###Python dependencies
* argcomplete
* flask
* pyyaml
* fabric
* python-daemon
* texttable

The Python dependencies can be installed by the [pip](https://pypi.python.org/pypi/pip) tool.

```shell
$ pip install [dependency]
```

The project includes ``PYTHON_REQUIREMENTS`` file that contains a list of tested and working versions of the required Python modules. A command to install the suggested versions of the Python requirements:
```shell
$ pip install -r PYTHON_REQUIREMENTS
```

### Configuration
The CLI needs the configuration files (groups.yaml, inventory.conf) in the program's directory to be placed. This project includes the example set of configuration files. Please copy the *.example files with the needed filenames as below.
<i>cp inventory.conf.example inventory.conf</i>
<i>cp groups.yaml.example groups.yaml</i>

[OFGW-mngt configuration files](#inventory-database)

### Autocomplete CLI feature (optional)
In order to use the autocomplete in CLI please go thru the [<b>argcomplete</b> installation instuction](https://pypi.python.org/pypi/argcomplete).

<b>Basic installation</b>
```shell
$ pip install argcomplete
$ activate-global-python-argcomplete
```

In order of errors insert a line like below into the <i>.bash.rc</i> file in your home directory.
```bash
eval "$(register-python-argcomplete my-awesome-script.py)"
```

Refresh your bash environment (start a new shell or <i>source /etc/profile</i>).

###Running
####Command Line Interface
```shell
$ ./ofgw_main.py --help
```

####RESTful service
```shell
$ ./daemon_ofgw_mngt.py [start|stop|restart]
```

Default HTTP service port: 5000
