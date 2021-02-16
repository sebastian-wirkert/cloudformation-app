
import json
import datetime
import boto3
import pymysql

client = boto3.client('sns')


def push_message(title, message, show, to=None):
    """
    set "to" to None to broadcast to everybody
    """
    x = {"sID": str(show),
         "title": title,
         "message": message,
         "to": to
         }

    return client.publish(
        TargetArn="arn:aws:sns:eu-west-1:229294447586:betsbyNotifier",
        Message=json.dumps({'default': json.dumps(x)}),
        MessageStructure='json'
    )


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def format_for_sql(param):
    if param is None:
        return "NULL"
    elif isinstance(param, str):
        param = param.replace("'", "''")
        return "\'" + param + "\'"
    else:
        return str(param)


def fsql(param):
    return format_for_sql(param)


def simple_sql_statements(conn, statements):
    """
    sequentially run statements and return last one as DictCursor
    """
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        try:
            for statement in statements:
                cur.execute(statement)
            result = cur.fetchall()
            conn.commit()
        #except pymysql.IntegrityError as err:
        #    return h.response("Error removing from database: {0}".format(err), 501)
        except pymysql.err.InterfaceError:
            conn.close()
    return result


def addQuestion(cur, question, answers, approved):
    aIDs = []
    for a in answers:
        cur.execute(f'INSERT INTO answers (aText, pic) VALUES ({fsql(a["aText"])}, {fsql(a["aPic"])});')
        aIDs.append(cur.lastrowid)
    q = question
    cur.execute("INSERT INTO questions (sID, qText, qStart, qEnd, qPic, points, originator, approved) " + \
                f"VALUES({q['sID']}, {fsql(q['qText'])}, {fsql(q['qStart'])}, {fsql(q['qEnd'])}, {fsql(q['qPic'])}, {q['points']}, {fsql(q['originator'])}, {approved});")
    qID = cur.lastrowid
    for aID in aIDs:
        cur.execute(f'INSERT INTO questionsAnswers (qID, aID) VALUES ({qID}, {aID});')
