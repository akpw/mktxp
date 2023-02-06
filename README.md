
![License](https://img.shields.io/badge/License-GNU%20GPL-blue.svg)
![Language](https://img.shields.io/badge/python-v3.6-blue)
![License](https://img.shields.io/badge/mikrotik-routeros-orange)
![License](https://img.shields.io/badge/prometheus-exporter-blueviolet)


## Description
MKTXP is a Prometheus Exporter for Mikrotik RouterOS devices.\
It gathers and exports a rich set of metrics across multiple routers, all easily configurable via built-in CLI interface. 

While simple to use, MKTXP also supports [advanced features](https://github.com/akpw/mktxp#advanced-features) such as automatic IP address resolution with support for both local & remote DHCP servers, concurrent exports across multiple router devices, configurable data processing & transformations, etc.

Apart from exporting to Prometheus, MKTXP can print selected metrics directly on the command line (see examples below). 

For effortless visualization of the RouterOS metrics exported to Prometheus, MKTXP comes with a dedicated [Grafana dashboard](https://grafana.com/grafana/dashboards/13679):

<img width="32%" alt="1" src="https://user-images.githubusercontent.com/5028474/217029083-3c2f561e-853f-45a7-b9f1-d818a830daf5.png"> <img width="32%" alt="2" src="https://user-images.githubusercontent.com/5028474/217029092-2b86b41b-1f89-4383-ac48-16652e820f7e.png"> <img width="32%" alt="3" src="https://user-images.githubusercontent.com/5028474/217029096-dbf6b46c-3ed7-4c76-a57b-8cebfb3b671c.png">


#### Requirements:
- Supported OSs:
   * Linux   
   * Mac OSX
   * FreeBSD

- Mikrotik RouterOS device(s)

- Optional: 
   * [Prometheus](https://prometheus.io/docs/prometheus/latest/installation/)
   * [Grafana](https://grafana.com/docs/grafana/latest/installation/)
   * [Docker](https://docs.docker.com/) / [Docker Compose](https://docs.docker.com/compose/)


## Install:
There are multiple ways to install this project, from a standalone app to a [fully dockerized monitoring stack](https://github.com/akpw/mktxp-stack). 
- with [MKTXP Stack](https://github.com/akpw/mktxp-stack): a ready-to-go MKTXP monitoring stack

- from [Docker image](https://github.com/akpw/mktxp/pkgs/container/mktxp) : `❯ docker pull ghcr.io/akpw/mktxp:latest`

- from [PyPI](https://pypi.org/project/mktxp/): `❯ pip install mktxp`

- latest from source repository: `❯ pip install git+https://github.com/akpw/mktxp`




## Getting started
To get started with MKTXP, you need to edit its main configuration file. This essentially involves adding your Mikrotik devices ip addresses & authentication info, optionally modifying various settings to specific needs. 

The default configuration file comes with a sample configuration, making it easy to copy / edit parameters as needed:
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

    installed_packages = True       # Installed packages
    dhcp = True                     # DHCP general metrics
    dhcp_lease = True               # DHCP lease metrics

    connections = True              # IP connections metrics
    connection_stats = False        # Open IP connections metrics 

    pool = True                     # Pool metrics
    interface = True                # Interfaces traffic metrics
    
    firewall = True                 # IPv4 Firewall rules traffic metrics
    ipv6_firewall = False           # IPv6 Firewall rules traffic metrics
    ipv6_neighbor = False           # Reachable IPv6 Neighbors

    poe = True                      # POE metrics
    monitor = True                  # Interface monitor metrics
    netwatch = True                 # Netwatch metrics
    public_ip = True                # Public IP metrics
    route = True                    # Routes metrics
    wireless = True                 # WLAN general metrics
    wireless_clients = True         # WLAN clients metrics
    capsman = True                  # CAPsMAN general metrics
    capsman_clients = True          # CAPsMAN clients metrics    

    user = True                     # Active Users metrics
    queue = True                    # Queues metrics
    
    remote_dhcp_entry = None        # An MKTXP entry for remote DHCP info resolution (capsman/wireless)

    use_comments_over_names = True  # when available, forces using comments over the interfaces names 
```

#### Local install
If you have a local MKTXP installation, you can edit this file with your default system editor directly from mktxp:
```bash
❯ mktxp edit
```
In case you prefer a different editor, run the ```edit``` command with its optional `-ed` parameter:
```
❯ mktxp edit -ed nano
```
Obviously, you can do the same via just opening the config file directly:
```
❯ nano ~/mktxp/mktxp.conf

```

#### Docker image install
For Docker instances, one way is to use a configured mktxp.conf file from a local installation. Alternatively you can create a standalone one in a dedicated folder:
```
mkdir mktxp
nano mktxp/mktxp.conf # copy&edit sample entry(ies) from above
```
Now you can mount this folder and run your docker instance with:
```
docker run -v "$(pwd)/mktxp:/home/mktxp/mktxp/" -p 49090:49090 -it --rm ghcr.io/akpw/mktxp:latest
```

#### MKTXP stack install
[MKTXP Stack Getting Started](https://github.com/akpw/mktxp-stack#install--getting-started) provides similar instructions around editing the mktxp.conf file and, if needed, adding a dedicated API user to your Mikrotik RouterOS devices as mentioned below.

💡 *In the case of usage within a [Docker Swarm](https://docs.docker.com/engine/swarm/), please do make sure to have all settings explicitly set in both the `mktxp.conf` and `_mktxp.conf` files.  Not doing this may cause [issues](https://github.com/akpw/mktxp/issues/55#issuecomment-1346693843) regarding a `read-only` filesystem.*

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

## MKTXP system configuration
In case you need more control on how MKTXP is run, it can be done via editing the `_mktxp.conf` file. This allows things like changing the port <sup>💡</sup> and other impl-related parameters, enable parallel router fetching and configurable scrapes timeouts, etc. 
As before, for local installation the editing can be done directly from mktxp:
```
mktxp edit -i
```

```
[MKTXP]
    port = 49090                    
    socket_timeout = 2
    
    initial_delay_on_failure = 120
    max_delay_on_failure = 900
    delay_inc_div = 5

    bandwidth = True                # Turns metrics bandwidth metrics collection on / off    
    bandwidth_test_interval = 420   # Interval for colllecting bandwidth metrics
    minimal_collect_interval = 5    # Minimal metric collection interval

    verbose_mode = False            # Set it on for troubleshooting

    fetch_routers_in_parallel = False   # Set to True if you want to fetch multiple routers parallel
    max_worker_threads = 5              # Max number of worker threads that can fetch routers (parallel fetch only)
    max_scrape_duration = 10            # Max duration of individual routers' metrics collection (parallel fetch only)
    total_max_scrape_duration = 30      # Max overall duration of all metrics collection (parallel fetch only)
```    
<sup>💡</sup> *When changing the default mktxp port for [docker image installs](https://github.com/akpw/mktxp#docker-image-install), you'll need to adjust the `docker run ... -p 49090:49090 ...` command to reflect the new port*

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


## Setting up MKTXP to run as a FreeBSD Service
If you've installed MKTXP on a FreeBSD system, you can run it with system boot via adding a service. \
Let's start with:


```
❯ nano /usr/local/etc/rc.d/mktxp
```

Now copy and paste the following:

```
#!/bin/sh

# PROVIDE: mktxp
# REQUIRE: DAEMON NETWORKING
# BEFORE: LOGIN
# KEYWORD: shutdown

# Add the following lines to /etc/rc.conf to enable mktxp:
# mktxp_enable="YES"
#
# mktxp_enable (bool):    Set to YES to enable mktxp
#                Default: NO
# mktxp_user (str):       mktxp daemon user
#                Default: root

. /etc/rc.subr

name=mktxp
rcvar=mktxp_enable 

: ${mktxp_enable:="NO"}
: ${mktxp_user:="root"}

# daemon
pidfile="/var/run/${name}.pid"
command="/usr/sbin/daemon"
mktxp_command="/usr/local/bin/mktxp export"
procname="daemon"
command_args=" -c -f -P ${pidfile} ${mktxp_command}"

load_rc_config $name 
run_rc_command "$1"
```

Let's save and then start the service as well as check on its' status:
```
❯ sudo sysrc mktxp_enable="YES"
❯ service mktxp start
❯ service mktxp status

❯ service mktxp status
mktxp is running as pid 36704
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
usage: MKTXP [-h] [--cfg-dir CFG_DIR] {info, edit, export, print, show, } ...

Prometheus Exporter for Mikrotik RouterOS

optional arguments:
  -h, --help            show this help message and exit
  --cfg-dir CFG_DIR     MKTXP config files directory (optional)
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

## Advanced features
While most of the [mktxp options](https://github.com/akpw/mktxp#getting-started) are self explanatory, some might require a bit of a context.

### Remote DHCP resolution
When gathering various IP address-related metrics, mktxp automatically resolves IP addresses whenever DHCP info is available. In many cases however, the exported devices does not have this information locally and instead rely on central DHCP servers. Since this could reduce readibility / usefulness of the metrics, mktxp supports remote DHCP server calls via the following option:
```
remote_dhcp_entry = None        # An MKTXP entry for remote DHCP info resolution in capsman/wireless
```
`MKTXP entry` in this context can be any other mktxp.conf entry, and for the sole purpose of providing DHCP info it does not even need to be enabled. 

### Connections stats
With many connected devices everywhere, one can often only guess where do they go to and what they actually do with all the information from your network environment. MKTXP let's you easily track those with a single option, with results available both from [mktxp dashboard](https://grafana.com/grafana/dashboards/13679-mikrotik-mktxp-exporter/) and the command line:

```
connection_stats = False        # Open IP connections metrics 
```
Setting this to `True` obviously enables the feature and allows to see something like that:

<img width="2346" alt="conns" src="https://user-images.githubusercontent.com/5028474/217042107-bffa0a81-a6a0-4474-87d4-1597cdd80735.png">

*Hey, what is this Temp&Humidity sensor has to do with a bunch of open network connections? 12 of them, really?*
*Let's go check on that in the dashboard, or just get the info right from the command line:*

```
❯ mktxp print -en MKT-GT -cn
+-------------------+--------------+------------------+-----------------------------------------------------------------------+
|     dhcp_name     | src_address  | connection_count |                             dst_addresses                             |
+===================+==============+==================+=======================================================================+
| T&H Cat's Room    | 10.20.10.149 |        12        |          3.124.97.151:32100(udp), 13.38.179.104:32100(udp),           |
|                   |              |                  |                       54.254.90.185:32100(udp)
```
*A quick `whois` check shows all of the external IPs relate to AWS, so supposedly it's legit... but let's remain vigilant, to know better :)*


### Parallel routers fetch
Concurrent exports across multiple devices can considerably speed up things for slow network connections. This feature can be turned on and configured with the following [system options](https://github.com/akpw/mktxp/blob/main/README.md#mktxp-system-configuration):
```
fetch_routers_in_parallel = False   # Set to True if you want to fetch multiple routers parallel
    max_worker_threads = 5              # Max number of worker threads that can fetch routers (parallel fetch only)
    max_scrape_duration = 10            # Max duration of individual routers' metrics collection (parallel fetch only)
    total_max_scrape_duration = 30      # Max overall duration of all metrics collection (parallel fetch only)
```
To keeps things within reliable boundaries, the last two parameters allows for controlling both individual and overall scrape durations


### mktxp port
By default, mktxp runs it's HTTP metrics endpoint on port 49090. You can change it via the following [system option](https://github.com/akpw/mktxp/blob/main/README.md#mktxp-system-configuration):
```
port = 49090 
```

## Installing Development version
- Clone the repo, then run: `$ python setup.py develop`


**Running Tests**
- TDB
- Run via: `$ python setup.py test`



