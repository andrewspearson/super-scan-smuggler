from argparse import ArgumentParser
from glob import glob
import json
import os
from tempfile import gettempdir
from time import time
from zipfile import ZipFile

from tenable.io import TenableIO
from tenable.sc import TenableSC

# Read arguments
args = ArgumentParser(description='Transfer scan data between multiple Tenable products')
args_group = args.add_mutually_exclusive_group(required=True)
args_group.add_argument('--config', metavar='<tenable.json>', dest='config_file', help='JSON config file')
args_group.add_argument('--config-gen', dest='config_gen', action='store_true', help='Generate a new JSON config file')
config_file = args.parse_args().config_file
config_gen = args.parse_args().config_gen

# Read or generate a JSON configuration file
config_file_name = 'tenable.json'
config_file_data = """{
  "downloads": {
    "tenable_io": [
      {
        "enabled": false,
        "id": "person@company.com",
        "access_key": "",
        "secret_key": "",
        "proxies": {"https": "127.0.0.1:8080"},
        "ssl_verify": true,
        "scan_ids": [100, 101, 102]
      }
    ],
    "tenable_sc": [
      {
        "enabled": false,
        "id": "person@tsc1.company.local",
        "host": "tsc1.company.local",
        "access_key": "",
        "secret_key": "",
        "proxies": {"https": "127.0.0.1:8080"},
        "ssl_verify": true,
        "scan_ids": [100, 101, 102]
      }
    ],
    "completed_within_days": 1,
    "nessus_files": [
      {
        "enabled": false,
        "directory": ""
      }
    ]
  },
  "uploads": {
    "tenable_io": [
      {
        "enabled": false,
        "id": "person@company2.com",
        "access_key": "",
        "secret_key": "",
        "proxies": null,
        "ssl_verify": true,
        "folder_id": 100,
        "dashboards": true
      }
    ],
    "tenable_sc": [
      {
        "enabled": false,
        "id": "person@tsc2.company.local",
        "host": "tsc2.company.local",
        "access_key": "",
        "secret_key": "",
        "proxies": null,
        "ssl_verify": true,
        "repository_id": 1,
        "dhcp": true,
        "virtual_hosts": false,
        "dead_hosts_wait": 0
      }
    ]
  }
}
"""
if config_file:
    if not os.path.isfile(config_file):
        print('ERROR: ' + config_file + ' does not exist. Use the --config-gen argument to create one.')
        exit()
    else:
        with open(config_file, 'r') as file:
            try:
                config = json.load(file)
            except ValueError:
                print('ERROR: Improperly formatted JSON configuration file')
                quit()
elif config_gen:
    if os.path.isfile('tenable.json'):
        print('ERROR: The tenable.json configuration file already exists and will NOT be overwritten.')
        exit()
    else:
        with open(config_file_name, 'w') as new_config_file:
            new_config_file.write(config_file_data)
        if not os.path.isfile(config_file_name):
            print('ERROR: Unable to write ' + config_file_name)
        else:
            print('INFO: Edit ' + config_file_name + ' for your environment')
        exit()
else:
    print('ERROR: Unrecognized input')
    exit()

# Get the Operating System's temp directory for temporary storage of Nessus files
temp_dir = gettempdir()


# Create a new class so SSL verification can be disabled
class TIO:
    def __init__(self, access_key, secret_key, proxies, ssl_verify):
        self.access_key = access_key
        self.secret_key = secret_key
        self.proxies = proxies
        self.ssl_verify = ssl_verify
        self.tio_client = TenableIO(self.access_key, self.secret_key, proxies=self.proxies)
        if self.ssl_verify is False:
            from warnings import filterwarnings
            filterwarnings('ignore', message='Unverified HTTPS request')
            self.tio_client._session.verify = False

    def scan_download(self, scan_id, completed_within_days):
        cutoff = int(time()) - (completed_within_days * 86400)
        history = self.tio_client.scans.history(int(scan_id), limit=1, pages=1)
        # read in all and decide which is eligible?
        history = list(history)
        if history[0]['status'] == 'completed' and history[0]['time_end'] > cutoff:
            file_path = os.path.join(temp_dir, str(scan_id) + '.nessus')
            with open(file_path, 'wb') as nessus_file:
                self.tio_client.scans.export(int(scan_id), history_id=history[0]['id'],
                                             format='nessus', fobj=nessus_file)
            if os.path.isfile(file_path):
                return file_path
            else:
                print('WARNING: Failed to export scan id ' + scan_id)

    def scan_upload(self, file_path, folder_id, dashboards):
        with open(file_path, 'rb') as nessus_file:
            self.tio_client.scans.import_scan(nessus_file, int(folder_id), aggregate=bool(dashboards))


# Create a new class for uniformity
class TSC:
    def __init__(self, host, access_key, secret_key, proxies, ssl_verify):
        self.host = host
        self.access_key = access_key
        self.secret_key = secret_key
        self.proxies = proxies
        self.ssl_verify = ssl_verify
        self.tsc_client = TenableSC(host, self.access_key, self.secret_key,
                                    proxies=self.proxies, ssl_verify=self.ssl_verify)

    def active_to_result(self, active_scan_ids, completed_within_days):
        active_scans = self.tsc_client.scans.list()
        cutoff = int(time()) - (completed_within_days * 86400)
        scan_results = self.tsc_client.scan_instances.list(start_time=cutoff)
        scan_result_ids = []
        for active_scan_id in active_scan_ids:
            active_scan_id = int(active_scan_id)
            for active_scan in active_scans['usable']:
                if active_scan_id == int(active_scan['id']):
                    for scan_result in scan_results['usable']:
                        if active_scan['name'] == scan_result['name']:
                            scan_result_details = self.tsc_client.scan_instances.details(scan_result['id'])
                            if scan_result_details['dataFormat'] in ['IPv4', 'agent'] and \
                                    scan_result_details['downloadAvailable'] == 'true' and \
                                    scan_result_details['downloadFormat'] == 'v2' and \
                                    scan_result_details['progress']['status'] == 'Completed' and \
                                    scan_result_details['resultSource'] == 'internal' and \
                                    scan_result_details['resultType'] in ['active', 'agents'] and \
                                    scan_result_details['running'] == 'false' and \
                                    scan_result_details['status'] == 'Completed':
                                scan_result_ids.append(int(scan_result['id']))
        return scan_result_ids

    def scan_download(self, scan_id_):
        nessus_files = []
        zip_file_path = os.path.join(temp_dir, str(scan_id_) + '.zip')
        with open(zip_file_path, 'wb') as zip_file:
            self.tsc_client.scan_instances.export_scan(scan_id_, fobj=zip_file, export_format='v2')
        with ZipFile(zip_file_path, 'r') as zip_file:
            for file_ in zip_file.namelist():
                if file_.endswith('.nessus'):
                    zip_file.extract(file_, temp_dir)
                    file_path = os.path.join(temp_dir, file_)
                if os.path.isfile(file_path):
                    nessus_files.append(file_path)
        os.remove(zip_file_path)
        return nessus_files

    def scan_upload(self, file_path, repository_id, dhcp, virtual_hosts, dead_hosts_wait):
        with open(file_path) as nessus_file:
            self.tsc_client.scan_instances.import_scan(nessus_file, int(repository_id), host_tracking=bool(dhcp),
                                                       vhosts=bool(virtual_hosts), auto_mitigation=int(dead_hosts_wait))


downloaded_nessus_files = {}
all_nessus_files = {}

# Download from Tenable.IO
for tio in config['downloads']['tenable_io']:
    if tio['enabled']:
        print('INFO: Downloading scans from ' + tio['id'])
        tio_client = TIO(tio['access_key'], tio['secret_key'], tio['proxies'], tio['ssl_verify'])
        downloaded_nessus_files[tio['access_key']] = []
        for scan_id in tio['scan_ids']:
            file_path = tio_client.scan_download(scan_id, config['downloads']['completed_within_days'])
            if file_path:
                downloaded_nessus_files[tio['access_key']].append(file_path)

# Download from Tenable.SC
for tsc in config['downloads']['tenable_sc']:
    if tsc['enabled']:
        print('INFO: Downloading scans from ' + tsc['id'])
        tsc_client = TSC(tsc['host'], tsc['access_key'], tsc['secret_key'], tsc['proxies'], tsc['ssl_verify'])
        scan_result_ids = tsc_client.active_to_result(tsc['scan_ids'], config['downloads']['completed_within_days'])
        downloaded_nessus_files[tsc['access_key']] = []
        for scan_result_id in scan_result_ids:
            file_paths = tsc_client.scan_download(scan_result_id)
            downloaded_nessus_files[tsc['access_key']].extend(file_paths)

# Push static Nessus file paths into list
all_nessus_files['static_file'] = []
for directory in config['downloads']['nessus_files']:
    if directory['enabled']:
        print('INFO: Loading scan files from ' + directory['directory'])
        for file_path in glob(directory['directory'] + '/*.nessus'):
            all_nessus_files['static_file'].append(file_path)

# Combine static Nessus files with downloaded Nessus files
all_nessus_files.update(downloaded_nessus_files)

if all_nessus_files:
    print('INFO: The following scans will be uploaded:')
    for key, file_paths in all_nessus_files.items():
        for file_path in file_paths:
            print('      ' + file_path)

else:
    print('INFO: There are no files to upload')
    print('INFO: Process complete')
    quit()

# Upload to Tenable.IO
for tio in config['uploads']['tenable_io']:
    if tio['enabled']:
        print('INFO: Uploading scans to ' + tio['id'])
        for access_key, file_paths in all_nessus_files.items():
            if access_key == tio['access_key']:
                pass
            else:
                tio_client = TIO(tio['access_key'], tio['secret_key'], tio['proxies'], tio['ssl_verify'])
                for file_path in file_paths:
                    tio_client.scan_upload(file_path, tio['folder_id'], tio['dashboards'])

# Upload to Tenable.SC
for tsc in config['uploads']['tenable_sc']:
    if tsc['enabled']:
        print('INFO: Uploading scans to ' + tsc['id'])
        for access_key, file_paths in all_nessus_files.items():
            if access_key == tsc['access_key']:
                pass
            else:
                tsc_client = TSC(tsc['host'], tsc['access_key'], tsc['secret_key'], tsc['proxies'], tsc['ssl_verify'])
                for file_path in file_paths:
                    tsc_client.scan_upload(file_path, tsc['repository_id'], tsc['dhcp'],
                                           tsc['virtual_hosts'], tsc['dead_hosts_wait'])

# Delete downloaded Nessus files from disk
if downloaded_nessus_files:
    print('INFO: Removing downloaded scan files from local disk')
    for access_key, file_paths in downloaded_nessus_files.items():
        for file_path in file_paths:
            try:
                os.remove(file_path)
            except OSError:
                print('WARNING: Unable to delete ' + file_path)

print('INFO: Process complete')
