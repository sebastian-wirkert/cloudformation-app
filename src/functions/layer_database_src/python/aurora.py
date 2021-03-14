
# Adapted from: https://github.com/aws-samples/amazon-rds-data-api-demo/blob/master/src/main/python/lambda_function_postgres.py
# Required imports
import os
import botocore
import boto3

DBSecretsStoreArn= os.environ["DBSecretsStoreArn"]
DBAuroraClusterArn= os.environ["DBAuroraClusterArn"]
DBName= os.environ["DBName"]

def my_execute_statement(sql_statement, param_set):
    rds_data = boto3.client('rds-data')
    return rds_data.execute_statement(
        resourceArn = DBAuroraClusterArn, 
        secretArn = DBSecretsStoreArn, 
        database = DBName, 
        sql = sql_statement,
        parameters = param_set,
        includeResultMetadata= True)

def create_parameter(name, value, param_type):
    typestring = "stringValue"
    if param_type=="int" or param_type=="long":
        typestring = "longValue"
    elif param_type=="bool":
        typestring = "booleanValue"
    elif param_type!="string":
        raise ValueError(f"param_type {param_type} not supported." +
            "currently has to be one of int, long, bool or string")
    return {'name': name, 'value': {typestring: value}}

def simple_call_rds_data_api(sql_statements, parameters=None):
    """
    Get a list of or one sql statement and execute them.
    Response is returned.
    """
    if parameters is None:
        parameters = []
    if isinstance(sql_statements, list):
        sql = ';'.join(sql_statements)
    else:
        sql = sql_statements
 
    response = my_execute_statement(sql, parameters)
    return response 

def to_python_dict(rds_response, which_columns=None):
    """
    Functionality inspired by:
    https://docs.aws.amazon.com/appsync/latest/devguide/resolver-util-reference.html#rds-helpers-in-util-rds
    """
    column_metadata = rds_response["columnMetadata"]
    records = rds_response["records"]
    column_names = [metadata['name'] for metadata in column_metadata]
    column_selector = [True]*len(column_names)
    if which_columns is not None:
        column_selector = [column_name in which_columns for column_name in column_names]
    
        
    formatted_records = [format_record(record, column_names, column_selector) for record in records]
    return formatted_records

def format_record(record, column_names, column_selector):
    formatted_record = {}
    for column_name, column, select in zip(column_names, record, column_selector):
        if select:
            formatted_record[column_name]= list(column.values())[0]
            if list(column.keys())[0] == "isNull":
                formatted_record[column_name] = None
    return formatted_record