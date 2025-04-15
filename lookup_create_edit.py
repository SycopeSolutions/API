#!/usr/bin/env python
# coding: utf-8

# Create or edit Lookups
# Script version: 1.0
# Tested on Sycope 3.1

import requests
import json
# Hiding SSL certificate warning messages
#from urllib3.exceptions import InsecureRequestWarning
#requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

#### Script Parameters

# Sycope website & credentials
host = 'https://192.168.1.14'
login = 'admin'
password = ''

null = None # workaround for defining null in JSON

api_command = '/npm/api/v1/config-element-lookup/csvFile'
lookupname = 'test-csv-file'
lookupid = '' # clearing the ID
lookupprivacy = 'Public' # Script supports Private and Public privacy
lookupvalues = [
    ["8.8.8.8", "Google DNS"],
    ["192.168.1.1", "Router"],
    ["192.168.1.100","Server"]
]
lookup = {
    "config": {
        "name": lookupname,
        "type": "csvFile",
        "active": True,
        "dataFile": "test-csv-file.csv",
        "delimiter": ",",
        "types": [
            "ip4",
            "string"
        ]
    },
    "file": {
        "columns": [
            "ip",
            "description"
        ],
        "rows": []
       
    }
    
}

lookup["file"]["rows"].extend(lookupvalues)

#For debugging
#print(json.dumps(lookup, indent=2))

### Creating new session
with requests.Session() as s: 
    
    payload={"username":login,"password":password}
    r = s.post(host+'/npm/api/v1/login',json=payload, verify=False)

    print('Searching in saved Lookups...')
    r = s.get(host+'/npm/api/v1/config-elements?offset=0&limit=2147483647&filter=category = "lookup.lookup"',json=payload, verify=False)
    all_data = r.json()["data"]

    #For debugging
    #print(json.dumps(all_data, indent=2))
    
    for result in all_data:
        if result['config']['name'] == lookupname:
            lookupid = result['id']
            savedtags = result['tags']
            print(f'Found Lookup "{lookupname}" with ID "{lookupid}".')

            r = s.get(f'{host}/npm/api/v1/config-element-lookup/csvFile/{lookupid}',json=payload, verify=False)
            savedlookup = r.json()

            #For debugging
            #print(json.dumps(savedlookup, indent=2))

            print('Checking data...')
            compare_config = sorted(lookup['config'].items()) == sorted(savedlookup['config'].items())
            compare_rows = sorted(lookup['file']['rows'], key=lambda x: str(x)) == \
                           sorted(savedlookup['file']['rows'], key=lambda x: str(x))
            
            #For debugging
            #print(f'compare_config: {compare_config}')
            #print(f'compare_rows: {compare_rows}')

            if compare_config == True and compare_rows == True:
                print(f'Saved data in the Lookup "{lookupname}" is identical to the input. No changes required.')
            else:
                lookup.update({
                    "attributes": {"defaultColumns": []},
                    "tags": None,
                    "id": lookupid,
                    "category": "lookup.lookup"
                })
    
                api_command = api_command + "/" + lookupid
    
                r = s.put(host+api_command,json=lookup, verify=False)
                data = r.json()
                
                if data['status'] == 200:
                    print(f'Data in the Lookup "{lookupname}" with ID "{lookupid}" have been successfully modified.')
                else:
                    #For debugging
                    print(r.json()) 
                
            break

    if lookupid == '':

        print(f'There are no Lookups with "{lookupname}" name. Creating new...')
        r = s.post(f'{host}/npm/api/v1/config-element-lookup/csvFile',json=lookup, verify=False)
        data = r.json()

        lookupid = data['id']

        if data['status'] == 200:
            print(f'New Lookup "{lookupname}" with ID "{lookupid}" has been created.')
        else:
            #For debugging
            print(r.json())

    # Let's check the privacy configuration
    print('Checking privacy...')

    r = s.get(f'{host}/npm/api/v1/permissions/CONFIGURATION.lookup.lookup/{lookupid}',json=lookup, verify=False)
    data = r.json()
    savedsidPerms = data['sidPerms']


    # Definition for Public Privacy
    sidPermsPublic = [
      {
        "sid": "ROLE_USER",
        "perms": [
          "VIEW"
        ]
      }
    ]
    # Definition for Private Privacy
    sidPermsPrivate = []

    # Checking defined Privacy in Sycope
    savedsidPermsValue = ''
    if savedsidPerms == sidPermsPublic: savedsidPermsValue = 'Public'
    if savedsidPerms == sidPermsPrivate: savedsidPermsValue = 'Private'

    #For debugging
    #print(json.dumps(data, indent=2))

    if lookupprivacy == 'Public' and savedsidPermsValue != 'Public':
        r = s.put(f'{host}/npm/api/v1/permissions/CONFIGURATION.lookup.lookup/{lookupid}',json=sidPermsPublic, verify=False)
        data = r.json()
        # Verifying if data was saved successfully
        if data['sidPerms'] == sidPermsPublic:
            print(f'Privacy for Lookup "{lookupname}" with ID "{lookupid}" has been modified to Public.')
        else:
            #For debugging
            print(r.json()) 

    elif lookupprivacy == 'Private' and savedsidPermsValue != 'Private':
        r = s.put(f'{host}/npm/api/v1/permissions/CONFIGURATION.lookup.lookup/{lookupid}',json=sidPermsPrivate, verify=False)
        data = r.json()
        # Verifying if data was saved successfully
        if data['sidPerms'] == sidPermsPrivate:
            print(f'Privacy for Lookup "{lookupname}" with ID "{lookupid}" has been modified to Private.')
        else:
            #For debugging
            print(r.json()) 
    elif savedsidPermsValue == '':
        print(f'Script could not identify the Privacy configuration in the Lookup "{lookupname}". Are you using custom Shared Privacy?')
    else:
        print(f'Privacy in the Lookup "{lookupname}" is identical to the input. No changes required.')
                
  
    # Closing the REST API session
    # Session should be automatically closed in session context manager
    r = s.get(host+'/npm/api/v1/logout', verify=False)
    s.close()
