import json

def handler(event, context):
    print(f"function with executed: {event}")
    return json.dumps({'sID': "100", 'sName': 'dummyshow', 'description': 'this is fake'})


