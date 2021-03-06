import argparse
import json
from pathlib import Path
import os

import yaml
import boto3

from src import util
from src.functions import upload_functions

# parameters until first function
allowed_stack_names = ["main-stack", "logic-stack"]

# load parameters
general_parameters = None
with open("src/parameters_general.yaml", 'r') as stream:
    general_parameters = yaml.safe_load(stream)
client = boto3.client('cloudformation', region_name=general_parameters['region'])
client_idp = boto3.client('cognito-idp', region_name=general_parameters['region'])

# load parameters passed to cloudfront
cloudformation_parameters= None
with open('src/parameters_cloudformation.json') as cf_parameters_file: 
    cloudformation_parameters = json.load(cf_parameters_file) 


def make_dummy_user():    
    stack_outputs = extract_our_stack_outputs()
    client_idp.sign_up(ClientId=stack_outputs['userPoolWebClientId'], Username='test@test.de', Password='testpw')
    client_idp.admin_confirm_sign_up(UserPoolId=stack_outputs['userPoolId'], Username='test@test.de')


def make_upload_functions():
    upload_functions.upload()


def make_delete_stack(stack_name):
    client.delete_stack(StackName=stack_name) 


def make_update_stack(stack_name, template_body): 
    make_change_stack(stack_name, template_body, client.update_stack)


def make_create_stack(stack_name, template_body):    
    make_change_stack(stack_name, template_body, client.create_stack)


def make_change_stack(stack_name, template_body_filename, method): 
    with open(template_body_filename, 'r') as template_file:
        template_body = template_file.read()
        update = method(StackName=stack_name, TemplateBody=template_body,
           Capabilities=["CAPABILITY_NAMED_IAM",], Parameters=cloudformation_parameters)
        print(update)


def make_describe_stacks(outpath=None):    
    stack_description = client.describe_stacks()
    if outpath:
        file_name = os.path.join(outpath, "stacks.json")    
        Path(outpath).mkdir(parents=True, exist_ok=True)
        with open(file_name, 'w') as fp:
            json.dump(stack_description, fp, indent=2, default=util.datetime_handler)
    return stack_description


def extract_stack_outputs(valid_stack_prefix=None):
    stack_description = make_describe_stacks()
    stacks = stack_description['Stacks']
    if valid_stack_prefix:
       	stacks = [stack for stack in stacks if valid_stack_prefix in stack['StackName']]
    stack_outputs = []
    for stack in stacks:
        stack_outputs.extend(stack['Outputs'])
    formatted_stack_outputs = cf_parameters_to_dict(stack_outputs, prefix='Output')
    return formatted_stack_outputs


def extract_our_stack_outputs():
    # iterate through our stack names to derive full stack names
    full_stack_names = [get_default_stack_parameters(stack_name)[0] for stack_name in allowed_stack_names]
    # take stack names to get stack outputs
    stack_outputs = [extract_stack_outputs(stack_name) for stack_name in full_stack_names]
    # merge all dicts to one
    all_stack_outputs = {}
    for stack_output in stack_outputs:
        all_stack_outputs.update(stack_output)
    return all_stack_outputs


def cf_parameters_to_dict(cf_parameters, prefix):
    return {parameter[f"{prefix}Key"]: parameter[f"{prefix}Value"] for parameter in cf_parameters}


def make_aws_config(outpath):    
    formatted_stack_outputs = extract_our_stack_outputs()    
    formatted_stack_outputs["identityPoolRegion"]=formatted_stack_outputs["region"]
    file_name = os.path.join(outpath, "aws_config.js")
    Path(outpath).mkdir(parents=True, exist_ok=True)
    with open(file_name, 'w') as fp:
        json_stack_outputs = json.dumps(formatted_stack_outputs, indent=2, default=util.datetime_handler)
        js_stack_outputs = f"const aws_config={json_stack_outputs}\nexport default aws_config"
        fp.write(js_stack_outputs)
    return formatted_stack_outputs


def get_default_stack_parameters(stack_name):
    if stack_name not in allowed_stack_names:
        raise ValueError(f"stack name should be one of ${allowed_stack_names}")
    cfp = cf_parameters_to_dict(cloudformation_parameters, prefix='Parameter')
    stack_prefix = f"{cfp['AppName']}-{cfp['Env']}"
    if stack_name == 'logic-stack':
        template_body = 'src/logic-cloudformation.yaml'
        stack_prefix += f"-{cfp['Color']}" # the logic stack can have versions, called colors
    elif stack_name == 'main-stack':
        template_body = 'src/main-cloudformation.yaml'
    full_stack_name = f"{stack_prefix}-{stack_name}"
    return full_stack_name, template_body


if __name__=="__main__":
    parser = argparse.ArgumentParser()    
    parser.add_argument('action',
                    choices=['update_stack', 'generate_aws_config', "describe_stack_config",
                             'create_stack', 'delete_stack', 'add_dummy_user',
                             'upload_functions'],
                    type=str,
                    help='what shall be done')
    parser.add_argument("--outpath", default='out', required=False, type=str,
        help="whereto outputs shall be written")    
    parser.add_argument("--stack_name", default='main-stack', required=False, type=str,
        help="name of the stack", choices=allowed_stack_names) 
    args = parser.parse_args()
    
    full_stack_name, template_body = get_default_stack_parameters(args.stack_name)
    
    if args.action=='generate_aws_config':
        make_aws_config(args.outpath)
    elif args.action=='describe_stack_config':
        make_describe_stacks(args.outpath)
    elif args.action=='update_stack':
        make_update_stack(full_stack_name, template_body)
    elif args.action=='create_stack':
        make_create_stack(full_stack_name, template_body)
    elif args.action=='delete_stack':
        make_delete_stack(full_stack_name)
    elif args.action=='upload_functions':
        make_upload_functions()
    elif args.action=='add_dummy_user':
        make_dummy_user()


