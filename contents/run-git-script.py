#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Author:  Oliver Roos
# Contact: https://twitter.com/roos_oliver

__author__ = 'Oliver Roos'
__version__ = '1.0.0'

import sys
import os
import platform
import requests
import argparse
from traceback import print_exc
import subprocess
import shlex
import urllib3

#-----------------------------------------------------------------------------#
# Global variables                                                            #
#-----------------------------------------------------------------------------#
DESCRIPTION = 'Download and run script from gitlab'

#-----------------------------------------------------------------------------#
# Arguments                                                                   #
#-----------------------------------------------------------------------------#
def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument(
        '-V', '--version',
        action='version',
        version='{0}: v{1} by {2}'.format('%(prog)s', __version__, __author__)
    )
    parser.add_argument(
        '-t', '--token',
        help='Gitlab Access token',
        dest='TOKEN',
        type=str,
    )
    parser.add_argument(
        '-p', '--projectid',
        help='Gitlab Project ID which hosts the file',
        dest='PROJECTID',
        type=int,
    )
    parser.add_argument(
        '-f', '--filepath',
        help='Path to script file from Gitlab project root directory',
        dest='FILEPATH',
        type=str,
    )
    parser.add_argument(
        '-a', '--arguments',
        help='All arguments that should be passed to the script',
        dest='ARGUMENTS',
        type=str,
    )
    parser.add_argument(
        '-u', '--baseuri',
        help='Gitlab base url',
        dest='BASEURI',
        type=str,
    )
    parser.add_argument(
        '-b', '--branch',
        help='Gitlab Branch',
        dest='BRANCH',
        default='master',
        type=str,
    )

    return parser.parse_args()

#-----------------------------------------------------------------------------#
# Main Script                                                                 #
#-----------------------------------------------------------------------------#

def run_powershell(scriptpath,arguments):
    if arguments is not None:
        cmd = ["PowerShell", "-ExecutionPolicy", "Bypass", "-File", scriptpath] + shlex.split(arguments)
    else:
        cmd = ["PowerShell", "-ExecutionPolicy", "Bypass", "-File", scriptpath]
    ec = subprocess.call(cmd)
    return("{0:d}".format(ec))

def run_bash(scriptpath, arguments):
    if arguments is not None:
        cmd = ['sh', scriptpath] + shlex.split(arguments)
    else:
        cmd = ['sh', scriptpath]
    ec = subprocess.call(cmd)
    return(ec)

def delete_files(scriptpath):
    try:
        os.remove(scriptpath)
    except SystemExit:
        sys.exit("Could not delete script file: ", scriptpath)

def main():

    # Parse arguments
    try:
        args = parse_args()
    except SystemExit:
        sys.exit(1)

    # Download file
    urllib3.disable_warnings()
    combined_url = args.BASEURI + '/api/v4/projects/' + str(args.PROJECTID) + '/repository/files/' + args.FILEPATH + '/raw?ref=' + args.BRANCH
    headers = {'PRIVATE-TOKEN': args.TOKEN}
    script = requests.get(combined_url, headers=headers, verify=False)

    # Save file to disk
    try:
        open(args.FILEPATH, 'wb').write(script.content)
    except SystemExit:
        sys.exit("Could not save script content to path: ", args.FILEPATH)

    # Run script from local copy
    if platform.system() == "Windows":
        
        try:
            script_result_code = run_powershell(".\\" + args.FILEPATH, args.ARGUMENTS)
            print(script_result_code)
        except SystemExit:
            delete_files(args.FILEPATH)
            sys.exit("Error running script on local system")
            
    elif platform.system() == "Linux":
        
        try:
            script_result_code = run_bash("./" + args.FILEPATH, args.ARGUMENTS)
            print(script_result_code)
        except SystemExit:
            delete_files(args.FILEPATH)
            sys.exit("Error running script on local system")
            
    else:
        delete_files(args.FILEPATH)
        sys.exit("Plattform not supported")

    # Delete script file after run
    delete_files(args.FILEPATH)

# Start program
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(1)

