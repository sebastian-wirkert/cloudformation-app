# Required imports
import json

import aurora

def handler(event, context):
    print(f"function executed with context: {context}")
    #print(f"function executed with event: {event}")
    response = aurora.simple_call_rds_data_api("select sName, sID, description, pic, picCounter from shows where sID=1", parameters=None)
    response = aurora.to_python_dict(response)
    if event["resolve"]== "query.getShow":
        response = response
    elif event["resolve"] == "mutation.deleteShow":
        response = {'sID': "100", 'sName': "fake delete", 'description': 'this is fake to test functionality'}

    return response


