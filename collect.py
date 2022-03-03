# encoding = utf-8
 
import os
import sys
import time
import datetime
import requests
import json
from datetime import datetime
 
def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # client_id = definition.parameters.get('client_id', None)
    # client_secret = definition.parameters.get('client_secret', None)
    pass
 
def collect_events(helper, ew):
    ## 1eme partie recup du token jwt
    global_tenant_id = helper.get_global_setting("tenant_id")
    global_client_id = helper.get_global_setting("client_id")
    global_client_secret = helper.get_global_setting("client_secret")
   
    helper.log_info("API collection started.")
   
    url = "https://login.microsoftonline.com/"+global_tenant_id+"/oauth2/v2.0/token"

    payload='scope=https%3A%2F%2Fgraph.microsoft.com%2F.default&grant_type=client_credentials&client_id='+global_client_id+'&client_secret='+global_client_secret
    
    headers = {
      'application': 'x-www-form-urlencoded',
      'Content-Type': 'application/x-www-form-urlencoded',
    }
   
    response = requests.request("POST", url, headers=headers, data=payload)
    # helper.log_info(response.text)
   
    r_json = json.loads(response.text)
    token = r_json["access_token"]
    # helper.log_info(r_json["access_token"])
   
    ## 2eme partie recup des events
       
    url = "https://graph.microsoft.com/v1.0/deviceManagement/managedDevices"

    payload={}
    headers = {
    'Authorization': 'Bearer ' + token
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    # helper.log_info(response.text)

    r_json = json.loads(response.text)
    r_status = response.status_code

    if r_status == 200 :
        if "@odata.nextLink" in r_json:
            pages = r_json['@odata.nextLink']
        for item in r_json["value"] :
            data = json.dumps(item)
            event = helper.new_event(source=helper.get_input_type(), index=helper.get_output_index(), sourcetype=helper.get_sourcetype(), data=data)
            # event = helper.new_event(source=opt_altospam_domain, index="main", sourcetype="altospam:api:test", data=data)
            ew.write_event(event)
        
        # Verification des pages suivantes (limit à 1000 results par page API Graph)
        while "@odata.nextLink" in r_json:
            url = pages
            payload={}
            headers = {
            'Authorization': 'Bearer ' + token
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            # helper.log_info(response.text)

            r_json = json.loads(response.text)
            r_status = response.status_code

            if r_status == 200:
                if "@odata.nextLink" in r_json:
                    pages = r_json['@odata.nextLink']
                for item in r_json["value"] :
                    data = json.dumps(item)
                    event = helper.new_event(source=helper.get_input_type(), index=helper.get_output_index(), sourcetype=helper.get_sourcetype(), data=data)
                    # event = helper.new_event(source=opt_altospam_domain, index="main", sourcetype="altospam:api:test", data=data)
                    ew.write_event(event)

    helper.log_info("Request successful")
    
    if r_status != 200 :
        helper.log_error("Request failed")
