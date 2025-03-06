
![License](https://img.shields.io/badge/License-GNU%20GPL-blue.svg)
![Language](https://img.shields.io/badge/python-v3.8-blue)
![License](https://img.shields.io/badge/mikrotik-routeros-orange)
![License](https://img.shields.io/badge/prometheus-exporter-blueviolet)


## Description
MKTXP is a Prometheus Exporter for Mikrotik RouterOS devices.\
It gathers and exports a rich set of metrics across multiple routers, all easily configurable via built-in CLI interface. 

While simple to use, MKTXP supports [advanced features](https://github.com/akpw/mktxp#advanced-features) such as automatic IP address resolution with both local & remote DHCP servers, concurrent exports across multiple router devices, configurable data processing & transformations, optional bandwidth testing, etc.

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
There are multiple ways to install this project, from a standalone app to a [fully dockerized monitoring stack](https://github.com/akpw/mktxp-stack). The supported options include:
- [MKTXP Stack](https://github.com/akpw/mktxp-stack): a ready-to-go MKTXP monitoring stack, with added Mikrotik centralized log processing based on a preconfigured syslog-ng / promtail / Loki stack.


- from [Docker image](https://github.com/akpw/mktxp/pkgs/container/mktxp) : `❯ docker pull ghcr.io/akpw/mktxp:latest`

- from [PyPI](https://pypi.org/project/mktxp/): `❯ pip install mktxp`

- latest from source repository: `❯ pip install git+https://github.com/akpw/mktxp`

- with the [sample Kubernetes deployment](deploy/kubernetes/deployment.yaml)


## Getting started
To get started with MKTXP, you need to edit its main configuration file. This essentially involves filling in your Mikrotik devices IP addresses & authentication info, optionally modifying various settings to specific needs. 

The default configuration file comes with a sample configuration, making it easy to copy / edit parameters for your RouterOS devices as needed:
```
[Sample-Router-1]
    # for specific configuration on the router level, overload the defaults here
    hostname = 192.168.88.1

[Sample-Router-2]
    # for specific configuration on the router level, overload the defaults here
    hostname = 192.168.88.2

[default]
    # this affects configuration of all routers, unless overloaded on their specific levels
    
    enabled = True          # turns metrics collection for this RouterOS device on / off
    hostname = localhost    # RouterOS IP address
    port = 8728             # RouterOS IP Port
    
    username = username     # RouterOS user, needs to have 'read' and 'api' permissions
    password = password
    
    use_ssl = False                 # enables connection via API-SSL servis
    no_ssl_certificate = False      # enables API_SSL connect without router SSL certificate
    ssl_certificate_verify = False  # turns SSL certificate verification on / off   
    plaintext_login = True          # for legacy RouterOS versions below 6.43 use False

    health = True                   # System Health metrics
    installed_packages = True       # Installed packages
    dhcp = True                     # DHCP general metrics
    dhcp_lease = True               # DHCP lease metrics

    connections = True              # IP connections metrics
    connection_stats = False        # Open IP connections metrics 

    interface = True                # Interfaces traffic metrics
    
    route = True                    # IPv4 Routes metrics
    pool = True                     # IPv4 Pool metrics
    firewall = True                 # IPv4 Firewall rules traffic metrics
    neighbor = True                 # IPv4 Reachable Neighbors
    dns = False                     # DNS stats

    ipv6_route = False              # IPv6 Routes metrics    
    ipv6_pool = False               # IPv6 Pool metrics
    ipv6_firewall = False           # IPv6 Firewall rules traffic metrics
    ipv6_neighbor = False           # IPv6 Reachable Neighbors

    poe = True                      # POE metrics
    monitor = True                  # Interface monitor metrics
    netwatch = True                 # Netwatch metrics
    public_ip = True                # Public IP metrics
    wireless = True                 # WLAN general metrics
    wireless_clients = True         # WLAN clients metrics
    capsman = True                  # CAPsMAN general metrics
    capsman_clients = True          # CAPsMAN clients metrics

    eoip = False                    # EoIP status metrics
    gre = False                     # GRE status metrics
    ipip = False                    # IPIP status metrics
    lte = False                     # LTE signal and status metrics (requires additional 'test' permission policy on RouterOS v6) 
    ipsec = False                   # IPSec active peer metrics
    switch_port = False             # Switch Port metrics

    kid_control_assigned = False    # Allow Kid Control metrics for connected devices with assigned users
    kid_control_dynamic = False     # Allow Kid Control metrics for all connected devices, including those without assigned user

    user = True                     # Active Users metrics
    queue = True                    # Queues metrics

    bgp = False                     # BGP sessions metrics
    routing_stats = False           # Routing process stats
    certificate = False             # Certificates metrics
   
    remote_dhcp_entry = None        # An MKTXP entry to provide for remote DHCP info / resolution
    remote_capsman_entry = None     # An MKTXP entry to provide for remote capsman info 

    use_comments_over_names = True  # when available, forces using comments over the interfaces names
    check_for_updates = False       # check for available ROS updates
```

Most options are easy to understand at first glance, and some are described in more details [later](https://github.com/akpw/mktxp#advanced-features).

<sup>💡</sup> To automatically migrate from the older `mktxp.conf` format in the existing installs, just set `compact_default_conf_values = True` in [the mktxp system config](https://github.com/akpw/mktxp#mktxp-system-configuration)

#### Local install
If you have a local MKTXP installation, you can edit the configuration file with your default system editor directly from mktxp:
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
For Docker instances, one way is to use a configured `mktxp.conf` file from a local installation. Alternatively you can create a standalone one in a dedicated folder:
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

<sup>💡</sup> *In the case of usage within a [Docker Swarm](https://docs.docker.com/engine/swarm/), please do make sure to have all settings explicitly set in both the `mktxp.conf` and `_mktxp.conf` files.  Not doing this may cause [issues](https://github.com/akpw/mktxp/issues/55#issuecomment-1346693843) regarding a `read-only` filesystem.*

## Mikrotik Device Config
For the purpose of RouterOS device monitoring, it's best to create a dedicated user with minimal required permissions. \
MKTXP only needs ```API``` and ```Read```<sup>💡</sup>, so at that point you can go to your router's terminal and type:
```
/user group add name=mktxp_group policy=api,read
/user add name=mktxp_user group=mktxp_group password=mktxp_user_password
```

<sup>💡</sup> *For the LTE metrics on RouterOS v6, the mktxp user will also need the `test` permission policy.*

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
    listen = '0.0.0.0:49090'         # Space separated list of socket addresses to listen to, both IPV4 and IPV6
    socket_timeout = 2
    
    initial_delay_on_failure = 120
    max_delay_on_failure = 900
    delay_inc_div = 5

    bandwidth = False               # Turns metrics bandwidth metrics collection on / off    
    bandwidth_test_interval = 600   # Interval for collecting bandwidth metrics
    minimal_collect_interval = 5    # Minimal metric collection interval

    verbose_mode = False            # Set it on for troubleshooting

    fetch_routers_in_parallel = False   # Fetch metrics from multiple routers in parallel / sequentially     
    max_worker_threads = 5              # Max number of worker threads that can fetch routers (parallel fetch only)
    max_scrape_duration = 10            # Max duration of individual routers' metrics collection (parallel fetch only)
    total_max_scrape_duration = 30      # Max overall duration of all metrics collection (parallel fetch only)

    compact_default_conf_values = False # Compact mktxp.conf, so only specific values are kept on the individual routers' level    
```    
<sup>💡</sup> *When changing the default mktxp port for [docker image installs](https://github.com/akpw/mktxp#docker-image-install), you'll need to adjust the `docker run ... -p 49090:49090 ...` command to reflect the new port*

## Grafana dashboard
Now with your RouterOS metrics being exported to Prometheus, it's easy to visualize them with this [Grafana dashboard](https://grafana.com/grafana/dashboards/13679)


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
When gathering various IP address-related metrics, MKTXP automatically resolves IP addresses whenever DHCP info is available. In many cases however, the exported devices do not have this information locally and instead rely on central DHCP servers. To improve readability / usefulness of the exported metrics, MKTXP supports remote DHCP server calls via the following option:
```
remote_dhcp_entry = None        # An MKTXP entry to provide for remote DHCP info / resolution
```
`MKTXP entry` in this context can be any other mktxp.conf entry, and for the sole purpose of providing DHCP info it does not even need to be enabled.  An example:
```
[RouterA]
    ...  # RouterA settings as normal

[RouterB]
    remote_dhcp_entry = RouterA  # Will resolve via RouterA
```

### Remote CAPsMAN info
Similar to remote DHCP resolution, mktxp allows collecting CAPsMAN-related metrics via the following option: 
```
    remote_capsman_entry = None     # An MKTXP entry to provide for remote capsman info
```
`MKTXP entry` in this context can be any other mktxp.conf entry, and for the sole purpose of collecting CAPsMAN-related metrics it does not even need to be enabled.  An example:
```
[RouterA]
    ...  # RouterA settings as normal

[RouterB]
    remote_capsman_entry = RouterA  # Will collect the CAPsMAN-related info via router A
```

### Connections stats
With many connected devices everywhere, one can often only guess where do they go to and what they actually do with all the information from your network environment. MKTXP let's you easily track those with a single option, with results available both from [mktxp dashboard](https://grafana.com/grafana/dashboards/13679-mikrotik-mktxp-exporter/) and the command line:

```
connection_stats = False        # Open IP connections metrics 
```
Setting this to `True` obviously enables the feature and allows to see something like that:

<img width="2346" alt="conns" src="https://user-images.githubusercontent.com/5028474/217042107-bffa0a81-a6a0-4474-87d4-1597cdd80735.png">

Hey, what is this Temp&Humidity sensor has to do with a bunch of open network connections? 12 of them, really?
Let's go check on that in the dashboard, or just get the info right from the command line:

```
❯ mktxp print -en MKT-GT -cn
+-------------------+--------------+------------------+-----------------------------------------------------------------------+
|     dhcp_name     | src_address  | connection_count |                             dst_addresses                             |
+===================+==============+==================+=======================================================================+
| T&H Cat's Room    | 10.20.10.149 |        12        |          3.124.97.151:32100(udp), 13.38.179.104:32100(udp),           |
|                   |              |                  |                       54.254.90.185:32100(udp)
```
*A few quick checks show all of the destination IPs relate to AWS instances, so supposedly it's legit... but let's remain vigilant, to know better :)*


### Parallel routers fetch
Concurrent exports across multiple devices can considerably speed up things for slow network connections. This feature can be turned on and configured with the following [system options](https://github.com/akpw/mktxp/blob/main/README.md#mktxp-system-configuration):
```
fetch_routers_in_parallel = False   # Set to True if you want to fetch multiple routers parallel
max_worker_threads = 5              # Max number of worker threads that can fetch routers (parallel fetch only)
max_scrape_duration = 10            # Max duration of individual routers' metrics collection (parallel fetch only)
total_max_scrape_duration = 30      # Max overall duration of all metrics collection (parallel fetch only)
```
To keeps things within expected boundaries, the last two parameters allows for controlling both individual and overall scrape durations


### mktxp endpoint listen addresses
By default, mktxp runs it's HTTP metrics endpoint on any IPv4 address on port 49090. However, it is also able to listen on multiple socket addresses, both IPv4 and IPv6. 
You can configure this behaviour via the following [system option](https://github.com/akpw/mktxp/blob/main/README.md#mktxp-system-configuration), setting ```listen``` to a space-separated list of sockets to listen to, e.g.:
```
listen = '0.0.0.0:49090 [::1]:49090'
```
A wildcard for the hostname is supported as well, and binding to both IPv4/IPv6 as available.

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

## Installing Development version
- Clone the repo, then run: `$ python setup.py develop`


**Running Tests**
- TDB
- Run via: `$ python setup.py test`
