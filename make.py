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


def make_describe_stacks(outpath):    
    client = boto3.client('cloudformation', region_name=general_parameters['region'])
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
                    choices=['generate_aws_config', "describe_stack_config"],
                    type=str,
                    help='what shall be done')
    parser.add_argument("--outpath", default='out', required=False, type=str,
        help="whereto outputs shall be written")
    args = parser.parse_args()
    
    if args.action=='generate_aws_config':
        make_aws_config(args.outpath)
    elif args.action=='describe_stack_config':
        make_describe_stacks(args.outpath)


