# Required imports
import json

import aurora

def handler(event, context):
    print(f"function executed with context: {context}")
    #print(f"function executed with event: {event}")
    response = aurora.simple_call_rds_data_api("select * from shows", parameters=None)
    print(response)
    dummyshow = "no show"
    if event["resolve"]== "query.getShow":
        dummyshow = "got Topmodel 2020"
    elif event["resolve"] == "mutation.deleteShow":
        dummyshow = "deleted Dschungecamp"

    return {'sID': "100", 'sName': dummyshow, 'description': 'this is fake to test functionality'}


