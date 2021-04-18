
![License](https://img.shields.io/badge/License-GNU%20GPL-blue.svg)
![Language](https://img.shields.io/badge/python-v3.6-blue)
![License](https://img.shields.io/badge/mikrotik-routeros-orange)
![License](https://img.shields.io/badge/prometheus-exporter-blueviolet)


## Description
MKTXP is a Prometheus Exporter for Mikrotik RouterOS devices.\
It gathers and exports a rich set of metrics across multiple routers, all easily configurable via built-in CLI interface. 

Apart from exporting to Prometheus, MKTXP can also print some of the metrics directly on the command line (see an example below).

For effortless visualization of the RouterOS metrics exported to Prometheus, MKTXP comes with a dedicated [Grafana dashboard](https://grafana.com/grafana/dashboards/13679):

<img src="https://akpw-s3.s3.eu-central-1.amazonaws.com/mktxp_black.png" width="400" height="620">


#### Requirements:
- [Python 3.6.x](https://www.python.org/downloads/release/python-360/) or later

- Supported OSs:
   * Linux
   * Mac OSX

- Mikrotik RouterOS device(s)

- Optional: 
   * [Prometheus](https://prometheus.io/docs/prometheus/latest/installation/)
   * [Grafana](https://grafana.com/docs/grafana/latest/installation/)


## Install:
- from [PyPI](https://pypi.org/project/mktxp/): `❯ pip install mktxp`
- latest from source repository: `❯ pip install git+https://github.com/akpw/mktxp`


## Getting started
After installing MKTXP, you need to edit its main configuration file. The easiest way to do it is via running:
```
❯ mktxp edit

```

This opens the config file in your default system editor. \
In case you prefer a different editor, just run the ```edit``` command with its optional `-ed` parameter. \
For example, to explicitly open the MKTXP config in nano:
```
❯ mktxp edit -ed nano

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
    firewall = True                 # Firewall rules matching traffic metrics
    monitor = True                  # Interface monitor metrics
    route = True                    # Routes metrics
    wireless = True                 # WLAN general metrics
    wireless_clients = True         # WLAN clients metrics
    capsman = True                  # CAPsMAN general metrics
    capsman_clients = True          # CAPsMAN clients metrics

    use_comments_over_names = False  # when available, forces using comments over the interfaces names 
```

## Mikrotik Device Config
For the purpose of RouterOS device monitoring, it's best to create a dedicated user with minimal required permissions. \
MKTXP only needs ```API``` and ```Read```, so at that point you can go to your router's terminal and type:
```
/user group add name=mktxp_group policy=api,read
/user add name=mktxp_user group=mktxp_group password=mktxp_user_password
```

## A check on reality
Now let's put some Mikrotik device address / user credentials in the above MKTXP configuration file, and at that point we should already be able to check out on our progress so far. Since MKTXP can output selected metrics directly on the command line with the ````mktxp print```` command, it's easy to do it even without Prometheus or Grafana. \
For example, let's go take a look at some of my smart home CAPsMAN clients:
```
 ❯ mktxp print -en MKT-GT -cc
Connecting to router MKT-GT@10.**.*.**
2021-01-24 12:04:29 Connection to router MKT-GT@10.**.*.** has been established

| dhcp_name            | dhcp_address   | mac_address       |   rx_signal | interface   | ssid   | tx_rate   | rx_rate   | uptime   |
|----------------------|----------------|-------------------|-------------|-------------|--------|-----------|-----------|----------|
| Woox Runner          | 10.**.*.**     | 80:*************D |         -64 | LR-2G-1-1   | AKP    | 72 Mbps   | 54 Mbps   | 3 days   |
| Woox Office Lamp     | 10.**.*.**     | 80:*************F |         -59 | LR-2G-1-1   | AKP    | 72 Mbps   | 54 Mbps   | 3 days   |
| Harmony Hub          | 10.**.*.**     | C8:*************5 |         -46 | LR-2G-1-1   | AKP    | 72 Mbps   | 72 Mbps   | 3 days   |
| Woox Office Hub      | 10.**.*.**     | DC:*************7 |         -44 | LR-2G-1-1   | AKP    | 72 Mbps   | 54 Mbps   | 3 days   |
| Woox Ext Hub         | 10.**.*.**     | DC:*************E |         -44 | LR-2G-1-1   | AKP    | 72 Mbps   | 54 Mbps   | 3 days   |
| Amazon Echo          | 10.**.*.**     | CC:*************4 |         -44 | LR-2G-1-1   | AKP    | 72 Mbps   | 72 Mbps   | a day    |
| Woox Living Room Hub | 10.**.*.**     | DC:*************0 |         -43 | LR-2G-1-1   | AKP    | 72 Mbps   | 54 Mbps   | 3 days   |
| JBL View             | 10.**.*.**     | 00:*************D |         -28 | LR-2G-1-1   | AKP    | 144 Mbps  | 117 Mbps  | 7 hours  |
|                      |                |                   |             |             |        |           |           |          |
| MBP15                | 10.**.*.**     | 78:*************E |         -53 | GT-5G-1     | AKP5G  | 877 Mbps  | 877 Mbps  | 3 days   |
|                      |                |                   |             |             |        |           |           |          |
| Woox Toaster         | 10.**.*.**     | 68:*************B |         -70 | KT-2G-1-1   | AKP    | 72 Mbps   | 54 Mbps   | 3 days   |
| Woox Kettle          | 10.**.*.**     | B4:*************5 |         -65 | KT-2G-1-1   | AKP    | 65 Mbps   | 54 Mbps   | 2 days   |
| Woburn White         | 10.**.*.**     | 54:*************6 |         -59 | KT-2G-1-1   | AKP    | 72 Mbps   | 72 Mbps   | 9 hours  |
| Siemens Washer       | 10.**.*.**     | 68:*************1 |         -57 | KT-2G-1-1   | AKP    | 72 Mbps   | 72 Mbps   | 2 days   |
| Woburn Black         | 10.**.*.**     | 54:*************8 |         -57 | KT-2G-1-1   | AKP    | 72 Mbps   | 72 Mbps   | 9 hours  |
| Google Nest Display  | 10.**.*.**     | 1C:*************A |         -49 | KT-2G-1-1   | AKP    | 52 Mbps   | 43 Mbps   | 8 hours  |
-----------------------  --
Connected Wifi Devices:  15
-----------------------  --
```
Hmmm, that toaster could probably use a better signal... :) \
But let's get back on track and proceed with the business of exporting RouterOS metrics to Prometheus.


## Exporting to Prometheus
For getting your routers' metrics into an existing Prometheus installation, we basically just need to connect MKTXP to it. \
Let's do just that via editing the Prometheus config file: 
```
❯ nano /etc/prometheus/prometheus.yml
```

and simply add:

```
  - job_name: 'mktxp'
    static_configs:
      - targets: ['mktxp_machine_IP:49090']

```

At that point, we should be all ready for running the main `mktxp export` command that will be gathering router(s) metrics as configured above and serving them to Prometheus via a http server on the default port 49090. \
````
❯ mktxp export
Connecting to router MKT-GT@10.**.*.**
2021-01-24 14:16:22 Connection to router MKT-GT@10.**.*.** has been established
Connecting to router MKT-LR@10.**.*.**
2021-01-24 14:16:23 Connection to router MKT-LR@10.**.*.** has been established
2021-01-24 14:16:23 Running HTTP metrics server on port 49090
````

In case a different port is preffered, it can be set as needed via running the ```mktxp edit -i``` command. \
That will open an internal MKTXP configuration file with some more implementation-related parameters.

## Grafana dashboard
Now with your RouterOS metrics being exported to Prometheus, it's easy to visualize them with this [Grafana dashboard](https://grafana.com/grafana/dashboards/13679)


## Setting up MKTXP to run as a Linux Service
If you've installed MKTXP on a Linux system, you can run it with system boot via adding a service. \
Let's start with:


```
❯ nano /etc/systemd/system/mktxp.service

```

Now copy and paste the following:

```
[Unit]
Description=MKTXP Exporter

[Service]
User=user # the user under which mktxp was installed
ExecStart=mktxp export # if mktxp is not at your $PATH, you might need to provide a full path

[Install]
WantedBy=default.target

```

Let's save and then start the service as well as check on its' status:
```
❯ sudo systemctl daemon-reload
❯ sudo systemctl start mktxp
❯ sudo systemctl enable mktxp

❯ systemctl status mktxp
● mktxp.service - MKTXP Mikrotik Exporter to Prometheus
     Loaded: loaded (/etc/systemd/system/mktxp.service; disabled; vendor preset: enabled)
     Active: active (running) since Sun 2021-01-24 09:16:44 CET; 2h 44min ago
     ...
```


## Description of CLI Commands
### mktxp commands
       . MKTXP commands:
        .. info     Shows base MKTXP info
        .. edit     Open MKTXP configuration file in your editor of choice        
        .. print    Displays selected metrics on the command line
        .. export   Starts collecting metrics for all enabled RouterOS configuration entries
        .. show   	Shows MKTXP configuration entries on the command line

````
❯ mktxp -h
usage: MKTXP [-h] {info, edit, export, print, show, } ...

````
To learn more about individual commands, just run it with ```-h```:
For example, to learn everything about ````mktxp show````:
````
❯ mktxp show -h
usage: MKTXP show [-h]
                  [-en ['Sample-Router']]
                  [-cfg]
Displays MKTXP config router entries
optional arguments:
  -h, --help            show this help message and exit
  -en, --entry-name ['Sample-Router']
                        Config entry name
  -cfg, --config        Shows MKTXP config files paths
````  

## Installing Development version
- Clone the repo, then run: `$ python setup.py develop`


**Running Tests**
- TDB
- Run via: `$ python setup.py test`



