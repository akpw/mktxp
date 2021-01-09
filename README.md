
![License](https://img.shields.io/badge/License-GNU%20GPL-blue.svg)
![Language](https://img.shields.io/badge/python-v3.6-blue)
![License](https://img.shields.io/badge/mikrotik-routeros-orange)
![License](https://img.shields.io/badge/prometheus-exporter-blueviolet)


<img src="http://www.akpdev.com/images/mktxp_b_t.png" width="460" height="600">



#### Requirements:
- [Python 3.6.x](https://www.python.org/downloads/release/python-360/) or later


- OSs:
    * Linux
    * Mac OSX
    * Windows: TBD / maybe

#### Install:
- from [PyPI](https://pypi.org/project/mktxp/): `$ pip install mktxp`
- latest from source repository: `$ pip install git+https://github.com/akpw/mktxp`


## Description
Prometheus Exporter for Mikrotik RouterOS. 
MKTXP enables gathering metrics across multiple RouterOS devices, all easily configurable via built-in CLI interface.
Comes with a dedicated [Grafana dashboard](https://grafana.com/grafana/dashboards/13679)


## Getting started
    Usage: $ mktxp [-h]
    	{info, version, show, add, edit, delete, start}
Commands:
  {info, version, show, add, edit, delete, start}

        $ mktxp {command} -h  #run this for detailed help on individual commands


## Full description of CLI Commands
### mktxp
      . action commands:
        .. start    Starts collecting metrics for all enabled RouterOS configuration entries
        .. add      Adds MKTXP RouterOS configuration entry
        .. show   	Shows MKTXP configuration entries
        .. delete   Deletes a MKTXP RouterOS configuration entry
        .. edit     Open MKTXP configuration file in your editor of choice
        .. info     Shows base MKTXP info
        .. version  Shows MKTXP version


## Installing Development version
- Clone the repo, then run: `$ python setup.py develop`

**Running Tests**
- TDB
- Run via: `$ python setup.py test`



