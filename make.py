import argparse
import json
from pathlib import Path
import os

import yaml
import boto3

from src import util

# load parameters
general_parameters = None
with open("parameters_general.yaml", 'r') as stream:
    general_parameters = yaml.safe_load(stream)
client = boto3.client('cloudformation', region_name=general_parameters['region'])

cloudformation_parameters= None
with open('parameters_cloudformation.json') as cf_parameters_file: 
    cloudformation_parameters = json.load(cf_parameters_file) 

def make_update_stack(stack_name, template_body):    
    with open(template_body, 'r') as template_file:
        template = template_file.read()
        update = client.update_stack(StackName=stack_name, TemplateBody=template,
            Capabilities=["CAPABILITY_NAMED_IAM",], Parameters=cloudformation_parameters)
        print(update)

def make_describe_stacks(outpath):    
    stack_description = client.describe_stacks()

    file_name = os.path.join(outpath, "stacks.json")    
    Path(outpath).mkdir(parents=True, exist_ok=True)
    with open(file_name, 'w') as fp:
        json.dump(stack_description, fp, indent=2, default=util.datetime_handler)
    return stack_description


def make_aws_config(outpath):    
    stack_description = make_describe_stacks(outpath)
    stacks = stack_description['Stacks']
    main_stack = [stack for stack in stacks if stack['StackName']=='main-stack']
    nr_main_stacks = len(main_stack)
    assert nr_main_stacks == 1, f"expected exactly 1 main-stack, got {nr_main_stacks}"
    main_stack = main_stack[0]
    stack_outputs = main_stack['Outputs']
    formated_stack_outputs = {output["OutputKey"]: output["OutputValue"] for output in stack_outputs}
    
    file_name = os.path.join(outpath, "aws_config.js")
    Path(outpath).mkdir(parents=True, exist_ok=True)
    with open(file_name, 'w') as fp:
        json_stack_outputs = json.dumps(formated_stack_outputs, indent=2, default=util.datetime_handler)
        js_stack_outputs = f"const aws_config={json_stack_outputs}\nexport default aws_config"
        fp.write(js_stack_outputs)
    return formated_stack_outputs

if __name__=="__main__":
    parser = argparse.ArgumentParser()    
    parser.add_argument('action',
                    choices=['update_stack', 'generate_aws_config', "describe_stack_config"],
                    type=str,
                    help='what shall be done')
    parser.add_argument("--outpath", default='out', required=False, type=str,
        help="whereto outputs shall be written")    
    parser.add_argument("--stack_name", default='main-stack', required=False, type=str,
        help="name of the stack")
    parser.add_argument("--template_body", default='main-cloudformation.yaml', required=False, type=str,
        help="the yaml file to describe the stack")
    args = parser.parse_args()
    
    if args.action=='generate_aws_config':
        make_aws_config(args.outpath)
    elif args.action=='describe_stack_config':
        make_describe_stacks(args.outpath)
    elif args.action=='update_stack':
        make_update_stack(args.stack_name, args.template_body)


