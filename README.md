
![License](https://img.shields.io/badge/License-GNU%20GPL-blue.svg)
![Language](https://img.shields.io/badge/python-v3.6-blue)
![License](https://img.shields.io/badge/mikrotik-routeros-orange)
![License](https://img.shields.io/badge/prometheus-exporter-blueviolet)


## Description
Prometheus Exporter for Mikrotik RouterOS. 
MKTXP enables gathering metrics across multiple RouterOS devices, all easily configurable via built-in CLI interface.
Comes with a dedicated [Grafana dashboard](https://grafana.com/grafana/dashboards/13679)

<img src="https://akpw-s3.s3.eu-central-1.amazonaws.com/mktxp_black.png" width="550" height="620">


#### Requirements:
- [Python 3.6.x](https://www.python.org/downloads/release/python-360/) or later

- Supported OSs:
   * Linux
   * Mac OSX

- Mikrotik RouterOS device(s)

- Optional: 
   * [Prometheus](https://prometheus.io/docs/prometheus/latest/installation/)
   * [Grafana](https://grafana.com/docs/grafana/latest/installation/)


#### Install:
- from [PyPI](https://pypi.org/project/mktxp/): `$ pip install mktxp`
- latest from source repository: `$ pip install git+https://github.com/akpw/mktxp`


## Getting started
After installing MKTXP, you need to edit its main configuration file. The easiest way to do it is via:
```
mktxp edit

```

This opens the file in your default system editor. In case you prefer a different editor, just run the ```edit``` command with its optional `-ed` parameter e.g.:
```
mktxp edit -ed nano

```

The configuration file comes with a sample configuration, making it easy to copy / edit parameters as needed:

```
[Sample-Router]
    enabled = False         # turns metrics collection for this RouterOS device on / off
    
    hostname = localhost    # RouterOS IP address
    port = 8728             # RouterOS IP Port
    
    username = username     # RouterOS user, needs to have 'read' and 'api' permissions
    password = password
    
    use_ssl = False                 # enables connection via API-SSL servis
    no_ssl_certificate = False      # enables API_SSL connect without router SSL certificate
    ssl_certificate_verify = False  # turns SSL certificate verification on / off   

    dhcp = True                     # DHCP general metrics
    dhcp_lease = True               # DHCP lease metrics
    pool = True                     # Pool metrics
    interface = True                # Interfaces traffic metrics
    firewall = True                 # Firewall rules traffic metrics
    monitor = True                  # Interface monitor metrics
    route = True                    # Routes metrics
    wireless = True                 # WLAN general metrics
    wireless_clients = True         # WLAN clients metrics
    capsman = True                  # CAPsMAN general metrics
    capsman_clients = True          # CAPsMAN clients metrics

    use_comments_over_names = False  # when available, forces using comments over the interfaces names 
```

## Mikrotik Device Config
For the purpose of device monitoring, it's best to create a dedicated RouterOS device user with minimal required permissions. MKTXP just needs ```API``` and ```Read```, so at that point you can go to your router and type something like:
```
/user group add name=mktxp_group policy=api,read
/user add name=mktxp_user group=mktxp_group password=mktxp_user_password
```
That's all it takes! Assuming you use the user info at the above configurtation file, at that point you already should be able to check your success with ```mktxp print``` command.


## Exporting to Prometheus
For exporting you router metrics to Prometheus, you need to connect MKTXP to it. To do that, open Prometheus config file: 
```
nano /etc/prometheus/prometheus.yml
```

and simply add:

```
  - job_name: 'mktxp'
    static_configs:
      - targets: ['mktxp_machine_IP:49090']

```

At that point, you should be are ready to go for running the `mktxp export` command that will get all router(s) metrics as configured above and serve them via http server on default port 49090. In case prefer to use a different port, you can change it (as well as other mktxp parameters) via running ```mktxp edit -i``` that opens internal mktxp settings file.

## Grafana dashboard
Now with all of your metrics in Prometheus, it's easy to visualise them with this [Grafana dashboard](https://grafana.com/grafana/dashboards/13679)


## Setting up MKTXP to run as a Linux Service
In case you install MKTXP on a Linux system and want to run it with system boot, just run

```
nano /etc/systemd/system/mktxp.service

```

and then copy and paste the following:

```
[Unit]
Description=MKTXP Exporter

[Service]
User=user # the user under which mktxp was installed
ExecStart=mktxp export # if mktxp is not at your $PATH, you might need to provide a full path

[Install]
WantedBy=default.target

```


## Full description of CLI Commands
### mktxp
      . action commands:
        .. info     Shows base MKTXP info
        .. edit     Open MKTXP configuration file in your editor of choice        
        .. export   Starts collecting metrics for all enabled RouterOS configuration entries
        .. print    Displays seleted metrics on the command line
        .. show   	Shows MKTXP configuration entries on the command line


Usage: $ mktxp [-h]
        {info, edit, export, print, show }
Commands:
  {info, edit, export, print, show }

        $ mktxp {command} -h  #run this for detailed help on individual commands



## Installing Development version
- Clone the repo, then run: `$ python setup.py develop`


**Running Tests**
- TDB
- Run via: `$ python setup.py test`



