import datetime

# copied json formater suited for boto3 from: https://gist.github.com/jeffbrl/67eed588f2d32afcaf3bf779bd91f7a7
def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")