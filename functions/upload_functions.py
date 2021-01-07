import os
import zipfile
import pathlib
import logging
import json

import boto3
from botocore.exceptions import ClientError

# zip all the subfolders (functions) in this folder. Needed to upload functions
# to s3 and deploy in cloudformation
# Run this script from project root directory

# we assume all folders within the scripts directory are functions
functions_directory = pathlib.Path(__file__).parent.absolute()

folders = os.listdir(functions_directory)
folders = [os.path.join(functions_directory, d) for d in folders]
existing_zip_folders = [d for d in folders if os.path.splitext(d)[1]=='.zip']
folders = [d for d in folders if os.path.isdir(d) and not d.endswith("__")]

s3_client = boto3.client('s3')
    
# cleanup existing zips
for zip_folders in existing_zip_folders:
    os.remove(zip_folders)

for f in folders:
    zip_file_name = os.path.basename(f) + '.zip'
    zip_file_path = os.path.join(functions_directory, zip_file_name)
    with zipfile.ZipFile(zip_file_path, 'w') as zippedfile:
        # Iterate over all the files in directory
        for folderName, subfolders, filenames in os.walk(f):
            for filename in filenames:
                #create complete filepath of file in directory
                filePath = os.path.join(folderName, filename)
                # Add file to zip
                zippedfile.write(filePath, os.path.basename(filePath))
    # upload to s3
    try:
        with open('parameters.json') as config_file:
            config_json = json.load(config_file)
            config_dict = {element['ParameterKey']:element['ParameterValue'] for element in config_json}
            response = s3_client.upload_file(zip_file_path, 
            config_dict["LambdaBucket"],
            f"{config_dict['LambdaFolder']}/{zip_file_name}")
    except ClientError as e:
        logging.error(e)
        logging.info("check if your aws account is configured")
logging.info("Function upload complete")