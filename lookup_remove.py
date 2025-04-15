#!/usr/bin/env python
# coding: utf-8

# Removing a Lookup
# Script version: 1.0
# Tested on Sycope 3.1

import requests
import json
import ipaddress
# Hiding SSL certificate warning messages
#from urllib3.exceptions import InsecureRequestWarning
#requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

#### Script Parameters

# Sycope website & credentials
host = 'https://192.168.1.14'
login = 'admin'
password = ''

lookupname = 'test-csv-file' # Please provide a Lookup name for removing
lookupid = ''

#For debugging
#print(json.dumps(lookup, indent=2))

### Creating new session
with requests.Session() as s: 
    
    payload={"username":login,"password":password}
    r = s.post(host+'/npm/api/v1/login',json=payload, verify=False)

    # Asking API for a list of all saved Lookups
    r = s.get(host+'/npm/api/v1/config-elements?offset=0&limit=2147483647&filter=category = "lookup.lookup"',json=payload, verify=False)
    all_data = r.json()["data"]

    #For debugging
    #print(json.dumps(all_data, indent=2))

    print('Searching in saved Lookups...')
    
    for result in all_data:
        if result['config']['name'] == lookupname:
            lookupid = result['id']
            savedtags = result['tags']
            print(f'Found Lookup "{lookupname}" with ID "{lookupid}".')

            r = s.delete(f'{host}/npm/api/v1/config-element/{lookupid}',json=payload, verify=False)
            job_run = r.json()
            
            print('Removing...')
            
            if job_run['status'] == 200:
                print(f'Lookup "{lookupname}" with ID "{lookupid}" has been removed.')
            else:
                #For debugging
                print(r.json()) 
            break

    if lookupid == '':

        print(f'There are no Lookups with "{lookupname}" name. Exiting.')
 
    # Closing the REST API session
    # Session should be automatically closed in session context manager
    r = s.get(host+'/npm/api/v1/logout', verify=False)
    s.close()
