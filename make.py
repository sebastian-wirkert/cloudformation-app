import argparse
import json
from pathlib import Path
import os

import yaml
import boto3

from src import util

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
    stack_outputs = extract_stack_outputs()
    client_idp.sign_up(ClientId=stack_outputs['userPoolClientID'], Username='test@test.de', Password='testpw')
    client_idp.admin_confirm_sign_up(UserPoolId=stack_outputs['userPoolID'], Username='test@test.de')


def make_delete_stack(stack_name):    
    client.delete_stack(StackName=stack_name) 


def make_update_stack(stack_name, template_body, use_parameters): 
    make_change_stack(stack_name, template_body, use_parameters, client.update_stack)


def make_create_stack(stack_name, template_body, use_parameters):    
    make_change_stack(stack_name, template_body, use_parameters, client.create_stack)


def make_change_stack(stack_name, template_body, use_parameters, method): 
    with open(template_body, 'r') as template_file:
        template = template_file.read()
        if use_parameters:
            update = method(StackName=stack_name, TemplateBody=template,
               Capabilities=["CAPABILITY_NAMED_IAM",], Parameters=cloudformation_parameters)
        else:
            update = method(StackName=stack_name, TemplateBody=template,
               Capabilities=["CAPABILITY_NAMED_IAM",])
        print(update)


def make_describe_stacks(outpath=None):    
    stack_description = client.describe_stacks()
    if outpath:
        file_name = os.path.join(outpath, "stacks.json")    
        Path(outpath).mkdir(parents=True, exist_ok=True)
        with open(file_name, 'w') as fp:
            json.dump(stack_description, fp, indent=2, default=util.datetime_handler)
    return stack_description


def extract_stack_outputs(stack_name='main-stack'):
    stack_description = make_describe_stacks()
    stacks = stack_description['Stacks']
    main_stack = [stack for stack in stacks if stack['StackName']==stack_name]
    nr_main_stacks = len(main_stack)
    assert nr_main_stacks == 1, f"expected exactly 1 main-stack, got {nr_main_stacks}"
    main_stack = main_stack[0]
    stack_outputs = main_stack['Outputs']
    formatted_stack_outputs = {output["OutputKey"]: output["OutputValue"] for output in stack_outputs}
    return formatted_stack_outputs


def make_aws_config(outpath):    
    formatted_stack_outputs = extract_stack_outputs()    
    formatted_stack_outputs["identityPoolRegion"]=formatted_stack_outputs["region"]
    file_name = os.path.join(outpath, "aws_config.js")
    Path(outpath).mkdir(parents=True, exist_ok=True)
    with open(file_name, 'w') as fp:
        json_stack_outputs = json.dumps(formatted_stack_outputs, indent=2, default=util.datetime_handler)
        js_stack_outputs = f"const aws_config={json_stack_outputs}\nexport default aws_config"
        fp.write(js_stack_outputs)
    return formatted_stack_outputs

if __name__=="__main__":
    parser = argparse.ArgumentParser()    
    parser.add_argument('action',
                    choices=['update_stack', 'generate_aws_config', "describe_stack_config",
                             'create_stack', 'delete_stack', 'add_dummy_user'],
                    type=str,
                    help='what shall be done')
    parser.add_argument("--outpath", default='out', required=False, type=str,
        help="whereto outputs shall be written")    
    parser.add_argument("--stack_name", default='main-stack', required=False, type=str,
        help="name of the stack")
    parser.add_argument("--template_body", default='src/main-cloudformation.yaml', required=False, type=str,
        help="the yaml file to describe the stack")
    parser.add_argument('--no_parameters', action='store_false') 
    args = parser.parse_args()
    
    if args.action=='generate_aws_config':
        make_aws_config(args.outpath)
    elif args.action=='describe_stack_config':
        make_describe_stacks(args.outpath)
    elif args.action=='update_stack':
        make_update_stack(args.stack_name, args.template_body, args.no_parameters)
    elif args.action=='create_stack':
        make_create_stack(args.stack_name, args.template_body, args.no_parameters)
    elif args.action=='delete_stack':
        make_delete_stack(args.stack_name)
    elif args.action=='add_dummy_user':
        make_dummy_user()


