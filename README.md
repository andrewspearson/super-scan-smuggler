# super-scan-smuggler
super-scan-smuggler.py will download scan files from multiple Tenable.IO and/or Tenable.SC systems, then upload those scans to multiple Tenable.IO and/or Tenable.SC systems. It can also read in static Nessus scan files stored on disk and upload those.

For a simpler, more user friendly version, see [scan-smuggler](https://github.com/andrewspearson/scan-smuggler). scan-smuggler will perform data transfers from one Tenable.IO system to one Tenable.SC system. super-scan-smuggler will perform data transfers among multiple systems and upload flat files, however, configuration is somewhat more complex.

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
#### View the help menu
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
#### Generate a configuration file
```
$ ./venv/bin/python super-scan-smuggler.py --config-gen

INFO: Edit tenable.json for your environment
```

#### ```tenable.json``` field descriptions
```
{
  "downloads": {                                # Download scan data from the following Tenable.IO and Tenable.SC instances
    "tenable_io": [                             # JSON array of Tenable.IO instances to pull scans from
      {
        "enabled": true,                        # Pull data from this instance of Tenable.IO
        "id": "",                               # This has no effect on the script. It is simply here so us humans can keep the instances straight.
        "access_key": "",                       # Tenable.IO access key
        "secret_key": "",                       # Tenable.IO secret key
        "proxies": {"https":  "127.0.0.1:8080"},# https://requests.readthedocs.io/en/master/user/advanced/#proxies
        "ssl_verify": true,                     # Enable or disable SSL verification
        "scan_ids": []                          # List of scan IDs to pull from Tenable.IO. You can get a scan ID by clicking on the scan in Tenable.IO and looking at the URL.
      }
    ],
    "tenable_sc": [                             # JSON array of Tenable.SC instances to pull scans from
      {
        "enabled": false,
        "id": "",
        "host": "",                             # Tenable.SC host address
        "access_key": "",
        "secret_key": "",
        "proxies": null,
        "ssl_verify": false,                    # Tenable.SC ships with a self-signed certificate
        "scan_ids": []                          # Scan IDs to pull from Tenable.SC. NOTE: These are scan IDs from "Active Scans", NOT "Scan Results". The script will find the right Scan Results to download.
      }
    ],
    "completed_within_days": 1,                 # Scans must have completed within x days to be downloaded. This ensures only fresh data is transfered.
    "nessus_files": [                           # JSON array of directories to pull scans from
      {
        "enabled": true,
        "directory": ""                         # Upload all .nessus files in this directory
      }
    ]
  },
  "uploads": {                                  # Now that scan files have been collected, upload the scans to the following systems
    "tenable_io": [                             # JSON array of Tenable.IO instances to upload the scans to
      {
        "enabled": true,
        "id": "",
        "access_key": "",
        "secret_key": "",
        "proxies": null,
        "ssl_verify": true,
        "folder_id": 10000,                     # Folder ID to upload scan data to. You can get the folder ID by looking at the URL in Tenable.IO.
        "dashboards": true                      # Include the uploaded scan data in the vulnerability workbench (aggregate)
      }
    ],
    "tenable_sc": [                             # JSON array of Tenable.SC instances to upload the scans to
      {
        "enabled": true,
        "id": "",
        "host": "",
        "access_key": "",
        "secret_key": "",
        "proxies": null,
        "ssl_verify": false,
        "repository_id": 1,                     # Repository ID to upload scans to
        "dhcp": true,                           # See Advanced setting descriptions here https://docs.tenable.com/tenablesc/Content/ActiveScanSettings.htm
        "virtual_hosts": false,                 # See Advanced setting descriptions here https://docs.tenable.com/tenablesc/Content/ActiveScanSettings.htm 
        "dead_hosts_wait": 0                    # See Advanced setting descriptions here https://docs.tenable.com/tenablesc/Content/ActiveScanSettings.htm
      }
    ]
  }
}
```


#### Completed ```tenable.json``` example
```json
{
  "downloads": {
    "tenable_io": [
      {
        "enabled": true,
        "id": "apearson@redacted.com",
        "access_key": "6974206973207765646e6573646179206d792064756465732121212121212121",
        "secret_key": "6974206973207765646e6573646179206d792064756465732121212121212121",
        "proxies": {"https":  "127.0.0.1:8080"},
        "ssl_verify": true,
        "scan_ids": [1, 2, 3, 4, 5]
      },
      {
        "enabled": false,
        "id": "apearson@redacted.com",
        "access_key": "",
        "secret_key": "",
        "proxies": null,
        "ssl_verify": true,
        "scan_ids": []
      }
    ],
    "tenable_sc": [
      {
        "enabled": true,
        "id": "apearson@tsc.corp.local",
        "host": "tsc.corp.local",
        "access_key": "6974206973207765646e657364617920",
        "secret_key": "6d792064756465732121212121212121",
        "proxies": null,
        "ssl_verify": false,
        "scan_ids": [6, 7, 8 ,9, 10]
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
        "directory": "/home/apearson/scan-files/ot"
      },
      {
        "enabled": true,
        "directory": "/home/apearson/scan-files/solarwinds"
      }
    ]
  },
  "uploads": {
    "tenable_io": [
      {
        "enabled": true,
        "id": "apearson@redacted.com",
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
        "id": "apearson@tsc.corp.local",
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

**IMPORTANT**: Change permissions on the configuration file so only the script can read your API keys.

#### Run the script
```
$ ./venv/bin/python /usr/local/bin/super-scan-smuggler/super-scan-smuggler.py --config /usr/local/bin/super-scan-smuggler/tenable.json 
INFO: Downloading scans from apearson@<redacted>
INFO: Downloading scans from apearson@<redacted>
INFO: Loading scan files from /home/person/scan-files/ot
INFO: Loading scan files from /home/person/scan-files/solarwinds
INFO: The following scans will be uploaded:
      /home/apearson/scan-files/ot/OT.nessus
      /home/apearson/scan-files/solarwinds/solarwinds.nessus
      /tmp/1.nessus
      /tmp/2.nessus
      /tmp/3.nessus
      /tmp/4.nessus
      /tmp/5.nessus
      /tmp/6.nessus
      /tmp/7.nessus
      /tmp/8.nessus
      /tmp/9.nessus
      /tmp/10.nessus
INFO: Uploading scans to apearson@<redacted>
INFO: Uploading scans to apearson@<redacted>
INFO: Removing downloaded scan files from local disk
INFO: Process complete
```
