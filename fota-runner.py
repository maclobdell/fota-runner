#!/usr/bin/env python 

# Pelion Device Management Demo - FOTA Helper
#

# Before running this script, make sure the following steps are completed
#   - initialize manifest tool & generate update certificate
#   - set Pelion API key 
#   - set app keys
#   - set wifi password
#   - compile application
#   - flash initial application, make sure it connects
#   - enroll the device if necessary

# Run this script from the top level of the Pelion example application

# This script does the following
#   1. modify verison in the file at  
#       - mbed-os/targets/TARGET_Cypress/TARGET_PSOC6/TARGET_CY8CKIT_064S2_4343W/secure_image_parameters.json
#   2. compile the application
#   3. start an update campaign on single device
#   4. checks completion (Not yet)

import argparse
import subprocess
import time
import os.path
import json
from os.path import join, abspath, dirname
from json import load, dump

# Call commands
def run_cmd(command):
    try:
        process = subprocess.Popen(command, bufsize=0, cwd=None)
        _stdout, _stderr = process.communicate()
    except Exception as e:
        print(("[OS ERROR] Command: \"%s\" (%s)" % (' '.join(command), e.args[0])))
        raise e

    return _stdout, _stderr, process.returncode

# Run demo step iteration
def run_demo_step(toolchain,target,profile,dryrun,multi):
    
    #todo - put this data into a separate configuration file
    parameters_file = "mbed-os/targets/TARGET_Cypress/TARGET_PSOC6/TARGET_CY8CKIT_064S2_4343W/secure_image_parameters.json"
    payload = "C:/pelion-psoc64/BUILD/CY8CKIT_064S2_4343W/ARM-RELEASE/pelion-psoc64_upgrade_signed.bin" 
    device_id = "016ef6f219fe00000000000100174596"
    fw_version_file = "app_version.h" 
    
#Up-Rev application        
    print("1 - Up-Rev Application")
    
    #open the params file, load data to json object
    with open(parameters_file, 'r', newline='\r\n') as f:
        param_data = json.loads(f.read())
            
    #locate "boot1" "VERSION"
    boot1_record = param_data["boot1"]
    fw_version = boot1_record["VERSION"]
    print("old fw version = " + fw_version)
    
    #convert version to number x.y
    new_fw_version = float(fw_version)
    new_fw_version = round(new_fw_version,1)

    #increase version
    new_fw_version = new_fw_version + 0.1            
    
    #round again to remove weird conversion problems
    new_fw_version = round(new_fw_version,1)

    fw_major_digit = str(int((float(new_fw_version)/1)))
    fw_minor_digit = str(int((float(new_fw_version)%1)*10))
    fw_patch_digit = "0"
    print("fw major digit = " + fw_major_digit)    
    print("fw minor digit = " + fw_minor_digit)    
    print("fw patch digit = " + fw_patch_digit)    
    
    #convert back to string
    new_fw_version = str(new_fw_version)
    print("new fw version = " + new_fw_version)
            
    #write old data to a backup file 
    s = json.dumps(param_data, indent=4)    
    with open (parameters_file + "_old.json", "w", newline='\r\n') as f:
        f.write(s)
        f.close()
        
    #modify file contents and write back
    boot1_record["VERSION"] = new_fw_version
    boot1_record["ROLLBACK_COUNTER"] = "0"
    param_data["boot1"] = boot1_record
    
    #save data to file
    s = json.dumps(param_data, indent=4)    
    with open (parameters_file, "w", newline='\r\n') as f:
        f.write(s)
        f.close()
    

    #open the app version file
    with open(fw_version_file, 'w') as f:
        f.write("#ifndef __APP_VERSION_H__\n")
        f.write("#define __APP_VERSION_H__\n")
        f.write("\n")
        f.write("#define APP_VERSION_MAJOR " + fw_major_digit + "\n")    
        f.write("#define APP_VERSION_MINOR " + fw_minor_digit + "\n")
        f.write("#define APP_VERSION_PATCH " + fw_patch_digit + "\n") 
        f.write("\n")
        f.write("#endif\n")
        f.close()  
      
#Compile
    print("2 - Compile New Application")
    
    cmd_compile = ["mbed", "compile", "-t", toolchain, "-m", target, "--profile", profile] 
    print("EXEC: %s" % ' '.join(cmd_compile))
    if dryrun is not True:
        _stdout, _stderr, _rc = run_cmd(cmd_compile)

    #FOTA    
    print("3 - Start Firmware Update Campaign")
 
    #todo - handle passing firwmare version correctly (uses only first digital after decimal?)
    
    #use only the tens digit (e.g. 9 instead of 3.9)
    
    if multi is True:
        #Multi-Device
        cmd_fota = ["manifest-tool", "update", "prepare", "-p", payload, "--fw-version", fw_minor_digit, "--no-cleanup"] 
    else:
        #Single-Device
        cmd_fota = ["manifest-tool", "update", "device", "-p", payload, "-D", device_id, "--fw-version", fw_minor_digit, "--no-cleanup"]

    print("EXEC: %s" % ' '.join(cmd_fota))
    if dryrun is not True:
        _stdout, _stderr, _rc = run_cmd(cmd_fota)
        
# script arguments
parser = argparse.ArgumentParser(description='Script to auto start pelion fota campaigns')
parser.add_argument("-t", "--toolchain", default="ARM", action='store', help="Specified toolchain(s).")
parser.add_argument("-m", "--mcu", default="CY8CKIT_064S2_4343W", action='store', help="Target microcontroller")
parser.add_argument("-u", "--multi", default=False, action='store_true', help="multi device update")
parser.add_argument("-d", "--dryrun", default=False, action='store_true', help="print commands, don't run them")
parser.add_argument("-p", "--profile", default="release", action='store', help="build profile")
parser.add_argument("-a", "--auto", default=False, action='store_true', help="auto mode")
parser.add_argument("-f", "--freq", default=6, action='store', help="num of fotas per hour in auto mode")

# The main thing
def main():

    args = parser.parse_args()
    current_path = os.getcwd()

    if args.auto is True:
        print("Run in a loop")
        #until interrupted, run the fota campaign at specific intervals
        while True:
            print('Executing FOTA at %s' % time.ctime())
            err = run_demo_step(args.toolchain,args.mcu,args.profile,args.dryrun,args.multi)
            # sleep for   60 / args.freq  minutes
            time.sleep(3600 / args.freq)        
    else:
        #Just run the step interation once
        print('Executing FOTA')
        err = run_demo_step(args.toolchain,args.mcu,args.profile,args.dryrun,args.multi)
    
        
if __name__ == '__main__':
    main()
