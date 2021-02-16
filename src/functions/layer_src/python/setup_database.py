import sys
import logging
import os

import pymysql

# rds settings
rds_host = os.environ["rdsHost"]
name = os.environ["dbUsername"]
password = os.environ["dbPasswort"]
db_name = os.environ["dbName"]

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
except:
    logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
    sys.exit()

logger.info("SUCCESS: Connection to RDS mysql instance succeeded")
