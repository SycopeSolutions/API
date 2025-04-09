#!/usr/bin/env python
# coding: utf-8

# Sending NQL query to Sycope with generated timestamps
# Script version: 1.0
# Tested on Sycope 3.0 stable

import requests
import time
import json
from datetime import datetime, timedelta
# Hiding SSL certificate warning messages
# from urllib3.exceptions import InsecureRequestWarning
# requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

#### Script Parameters

# Sycope website & credentials
host = 'https://192.168.1.14'
login = 'admin'
password = ''

# Query for discovered services in specific asset (Asset Discovery)
#query = 'src stream="assetNetflowAggr" | aggr total=count(1) by serverPort as serverPortName, lookup("app", "name", {"ip": serverIp, "port": serverPort}) as appName unwind=true | sort serverPortName asc | limit 1000'

# Query for netflowByAppsAggr stream (Visibility)
#query = 'src stream="netflowByAppsAggr" | limit 1000'

# Query for Alerts
query = 'src stream="alerts"'

### Creating new session
with requests.Session() as s: 
    payload={"username":login,"password":password}
    r = s.post(host+'/npm/api/v1/login',json=payload, verify=False)
    
    ### Defining timestamps

    # Current date will be used for End Time
    now = datetime.now().astimezone().isoformat('T', 'seconds')
    endTime = "@"+now
    # For debugging
    # print("endTime =", endTime)

    # Last Hour will be used for Start Time
    startTime = datetime.now() - timedelta(hours = 1)
    startTime = startTime.astimezone().isoformat('T', 'seconds')
    startTime = "@"+startTime
    # For debugging
    # print("startTime =", startTime)
    
    ### Sending NQL query (HTTPS POST) to find ID of the requested IP address
    ### Output will include jobId
    off_size = 50000
    payload= {
      "startTime": startTime,
      "endTime": endTime,
      "nql": query,
      "fsActive": False,
      "waitTime": 30000,
      "limit": off_size
    }
    
    r = s.post(host+'/npm/api/v1/pipeline/run',json=payload, verify=False)
    job_run = r.json()

    # For debugging
    # print(r.json())
    
    ### Gathering query output using jobId
    all_data = []
    for offset in range(job_run["data"]["total"]//off_size+1):
        #print(offset) # for debugging
        payload = {
          "limit": off_size,
          "offset": offset*off_size
        }
        r = s.post(f'{host}/npm/api/v1/pipeline/{job_run["jobId"]}/data',json=payload, verify=False)
        chunk = r.json()
        all_data.extend(chunk["data"])
    
    # API response
    print(all_data)

    # For debugging (pretty table)
    #import pandas as pd
    #pd.set_option('display.min_rows', 500)
    #pd.set_option('display.max_rows', 500)
    #df = pd.DataFrame(all_data)
    #print(df) 

    # Closing the REST API session
    # Session should be automatically closed in session context manager
    r = s.get(host+'/npm/api/v1/logout', verify=False)
    s.close()
