# super-scan-smuggler
super-scan-smuggler.py downloads scan data from multiple Tenable products and then uploads it to multiple Tenable products. This script can also upload static .nessus files that might be saved on disk.
## Requirements
* python3
* [pyTenable](https://github.com/tenable/pyTenable)
## Installation
### Create a Python virtual environment
```
$ git clone https://github.com/andrewspearson/super-scan-smuggler.git /usr/local/bin/super-scan-smuggler
$ python3 -m venv /usr/local/bin/super-scan-smuggler/venv
$ . /usr/local/bin/super-scan-smuggler/venv/bin/activate
$ pip install -r requirements.txt
$ deactivate
```
### Create a cron entry (optional)
```
$ crontab -l

0 8 * * * /usr/local/bin/super-scan-smuggler/venv/bin/python /usr/local/bin/super-scan-smuggler/super-scan-smuggler.py --config /usr/local/bin/super-scan-smuggler/tenable.ini
```
## Usage
View the help menu
```
$ cd /usr/local/bin
$ ./venv/bin/python scan-smuggler.py -h

usage: super-scan-smuggler.py [-h] (--config <tenable.json> | --config-gen)

Transfer scan data between multiple Tenable products

optional arguments:
  -h, --help            show this help message and exit
  --config <tenable.json>
                        JSON config file
  --config-gen          Generate a new JSON config file
```
Generate a configuration file
```
$ ./venv/bin/python super-scan-smuggler.py --config-gen

INFO: Edit tenable.json for your environment
```
Edit the configuration file for your environment. Please be familiar with [JSON](https://en.wikipedia.org/wiki/JSON) data types before editing. Here is an example ```tenable.json``` configuration file:
```json
{
  "downloads": {
    "tenable_io": [
      {
        "enabled": true,
        "id": "person@company.com",
        "access_key": "6974206973207765646e6573646179206d792064756465732121212121212121",
        "secret_key": "6974206973207765646e6573646179206d792064756465732121212121212121",
        "proxies": {"https":  "127.0.0.1:8080"},
        "ssl_verify": true,
        "scan_ids": [100, 101, 102]
      },
      {
        "enabled": false,
        "id": "person@company2.com",
        "access_key": "",
        "secret_key": "",
        "proxies": null,
        "ssl_verify": true,
        "scan_ids": [200, 201, 202]
      }
    ],
    "tenable_sc": [
      {
        "enabled": true,
        "id": "person@tsc.corp.local",
        "host": "tsc.corp.local",
        "access_key": "6974206973207765646e657364617920",
        "secret_key": "6d792064756465732121212121212121",
        "proxies": null,
        "ssl_verify": false,
        "scan_ids": []
      },
      {
        "enabled": false,
        "id": "",
        "host": "",
        "access_key": "",
        "secret_key": "",
        "proxies": null,
        "ssl_verify": false,
        "scan_ids": []
      }
    ],
    "completed_within_days": 1,
    "nessus_files": [
      {
        "enabled": true,
        "directory": "/home/person/scan-files/mdm"
      },
      {
        "enabled": false,
        "directory": "/home/person/scan-files/malware"
      }
    ]
  },
  "uploads": {
    "tenable_io": [
      {
        "enabled": true,
        "id": "person@company.com",
        "access_key": "6974206973207765646e6573646179206d792064756465732121212121212121",
        "secret_key": "6974206973207765646e6573646179206d792064756465732121212121212121",
        "proxies": null,
        "ssl_verify": true,
        "folder_id": 10000,
        "dashboards": true
      }
    ],
    "tenable_sc": [
      {
        "enabled": true,
        "id": "person@tsc.corp.local",
        "host": "tsc.corp.local",
        "access_key": "6974206973207765646e657364617920",
        "secret_key": "6d792064756465732121212121212121",
        "proxies": null,
        "ssl_verify": false,
        "repository_id": 1,
        "dhcp": true,
        "virtual_hosts": false,
        "dead_hosts_wait": 0
      }
    ]
  }
}
```
IMPORTANT: Be sure to change permissions on the configuration file so everyone cannot read your API keys.

Run the script
```
$ ./venv/bin/python /usr/local/bin/super-scan-smuggler/super-scan-smuggler.py --config /usr/local/bin/super-scan-smuggler/tenable.json 
INFO: Downloading scans from apearson@<obfuscated>
INFO: Downloading scans from apearson@<obfuscated>
INFO: Loading scan files from /home/person/scan-files/malware
INFO: Loading scan files from /home/person/scan-files/mdm
INFO: Loading scan files from /home/person/scan-files/ot
INFO: Loading scan files from /home/person/scan-files/solarwinds
INFO: Loading scan files from /home/person/scan-files/struts
INFO: The following scans will be uploaded:
      /home/person/scan-files/malware/nessus_report_7.nessus
      /home/person/scan-files/malware/nessus_report_12.nessus
      /home/person/scan-files/malware/nessus_report_10.nessus
      /home/person/scan-files/malware/nessus_report_9.nessus
      /home/person/scan-files/malware/nessus_report_5.nessus
      /home/person/scan-files/malware/nessus_report_1.nessus
      /home/person/scan-files/malware/nessus_report_3.nessus
      /home/person/scan-files/malware/nessus_report_6.nessus
      /home/person/scan-files/malware/nessus_report_8.nessus
      /home/person/scan-files/malware/nessus_report_4.nessus
      /home/person/scan-files/malware/nessus_report_11.nessus
      /home/person/scan-files/malware/nessus_report_2.nessus
      /home/person/scan-files/mdm/AirWatch_MDM-4Assets.nessus
      /home/person/scan-files/mdm/AirWatch_MDM-3Assets.nessus
      /home/person/scan-files/ot/OT_Data_Import-export.nessus
      /home/person/scan-files/solarwinds/sunburst-export2.nessus
      /home/person/scan-files/solarwinds/Solarwinds_Orion_VCF-export.nessus
      /home/person/scan-files/solarwinds/SUPERNOVA_plugin_test-export.nessus
      /home/person/scan-files/struts/Struts.nessus
      /tmp/33.nessus
      /tmp/37.nessus
      /tmp/2247.nessus
      /tmp/4290.nessus
      /tmp/4292.nessus
      /tmp/4733.nessus
      /tmp/2366.nessus
      /tmp/2368.nessus
      /tmp/2375.nessus
      /tmp/2377.nessus
INFO: Uploading scans to apearson@<obfuscated>
INFO: Uploading scans to apearson@<obfuscated>
INFO: Removing downloaded scan files from local disk
INFO: Process complete
```
