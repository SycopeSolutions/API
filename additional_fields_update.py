#!/usr/bin/env python
# coding: utf-8

# Modifying Additional Fields in Asset Discovery
# Script version: 1.0
# Tested on Sycope 3.0 stable

import requests
import json
import ipaddress
# Hiding SSL certificate warning messages
# from urllib3.exceptions import InsecureRequestWarning
# requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

#### Script Parameters

# IP Address for saving Additional Fields in Asset Discovery
ipAsset = '192.168.1.38'
# Sycope website & credentials
host = 'https://192.168.1.14'
login = 'admin'
password = ''
# Defining Additional Fields
additional = {"field1":"test",  
              "field2":"test"}

# Checking if IP address is valid (IPv4 or IPv6)
valid_ip_address = ipaddress.ip_address(ipAsset)

### Creating new session
with requests.Session() as s: 
    payload={"username":login,"password":password}
    r = s.post(host+'/npm/api/v1/login',json=payload, verify=False)
    
    ### Sending NQL query (HTTPS POST) to find ID of the requested IP address
    ### Output will include jobId
    query = f'src stream="assetDevices" | ip = "{ipAsset}"'
    off_size = 10
    payload= {
      "nql": query,
      "fsActive": False,
      "waitTime": 30000,
      "limit": off_size
    }
    
    r = s.post(host+'/npm/api/v1/pipeline/run',json=payload, verify=False)
    job_run = r.json()
    
    ### Gathering query output using jobId
    payload = {
      "limit": off_size,
      "offset": 0
    }
    r = s.post(f'{host}/npm/api/v1/pipeline/{job_run["jobId"]}/data',json=payload, verify=False)
    all_data = r.json()["data"]
    
    
    # Checking number of rows in the output (there should be only one)
    n_rows = len(all_data)
    if(n_rows > 1 ):
        raise Exception(f'Output has duplicate IP addresses ({n_rows}). Please investigate.')
    elif n_rows ==0:
        raise Exception(f'IP {ipAsset} has not been found in Asset Devices. Please investigate.')

    
    # Gathering only the first entry (fail safe)
    ids = [value['id'] for value in all_data]
    asset_id = ids[0]
    
    # Example for clearing Additional Fields
    # payload = {}
    
    ### Sending API request (HTTPS PUT) for changing Additional Fields
    r = s.put(host+'/npm/api/v1/inventory/device/'+asset_id+'/additional',json=additional, verify=False)
    
    # For debugging
    # Example of API response:
    # {'id': '64d7e9c6-ce1777b0-be88fd5f', 'name': None, 'domainName': None, 'ip': '192.168.1.38', 'description': None, 'timestamp': 1732476606653, 'tags': None, 'additional': {'field2': 'test', 'field1': 'test'}, 'dnsRecords': []}
    # print(r.json())
    
    # For debugging (pretty table)
    # import pandas as pd
    # pd.DataFrame(all_data)
    
    # Checking saved data and comparing it
    if(r.json().get('additional') == additional):
        print(f'Additional Field for IP {ipAsset} has been saved successfully.')
    else:
        print("Something went wrong.")
    
    # Closing the REST API session
    # Session should be automatically closed in session context manager
    r = s.get(host+'/logout', verify=False)
    s.close()
