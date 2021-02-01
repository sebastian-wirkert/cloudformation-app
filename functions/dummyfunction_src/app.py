import json

def handler(event, context):
    print(f"function with executed: {event}")
    dummyshow = "no description"
    if event.field == "getShow":
        dummyshow = "got Topmodel 2020"
    elif event.field == "deleteShow":
        dummyshow = "deleted Dschungecamp"

    return {'sID': "100", 'sName': dummyshow, 'description': 'this is fake'}


