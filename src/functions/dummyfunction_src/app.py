import json

def handler(event, context):
    print(f"function executed with context: {context}")
    #print(f"function executed with event: {event}")
    dummyshow = "no show"
    if event["resolve"]== "query.getShow":
        dummyshow = "got Topmodel 2020"
    elif event["resolve"] == "mutation.deleteShow":
        dummyshow = "deleted Dschungecamp"

    return {'sID': "100", 'sName': dummyshow, 'description': 'this is fake to test functionality'}

