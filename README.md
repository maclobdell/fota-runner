# PSoC 64 Firmware Update Demo Runner

This is a relatively simple script to automaticaly run Firmware update Over The Air (fota) campaigns with Pelion device management.  It relies on a specific Mbed OS + Pelion example application for Cypress PSoC 64.

This script is designed to run from the top level of the Pelion example application 'psoc64-demo'.  

 This script does the following
* Update the firmware version in two locations by modifying the files at:  
    * mbed-os/targets/TARGET_Cypress/TARGET_PSOC6/TARGET_CY8CKIT_064S2_4343W/secure_image_parameters.json
    * app_version.h
* compile the application
* Create a manifest for the firmware update 
* start an update campaign on single device (note that if you want to run a firmware update campaign on multiple devices, you can generate the manifest with this script, see -u option below, then create the update campaign your self manually).

## Dependencies
* Mbed OS 5.15 or later
* Mbed CLI 1.10 or later  
* Python 3.6.x or later

## Before you begin
* It's a good idea to be familiar with Mbed OS and its tools in order to use this script
* Make sure the tools listed above are installed
* Also, you need to review the Pelion Workshop Training slides for using Pelion with PSoC 64

## Demo Setup 
Before running this script, make sure the following steps are completed
* Import the Pelion device management example application for PSoC64
```
mbed import https://github.com/maclobdell/psoc64-demo
cd psoc64-demo
```
* Put fota-runner.py in the root directory of the application `psoc64-demo`
* Follow the instructions in the readme file of the `psoc64-demo` repo
* Update the arguments in fota-runner.py for the following parameters
    * parameters_file - location to `secure_image_parameters.json` file for cypress target which contains the firmware application version
    * payload - location of the binary file used in update campaign.  Should be something like `<project name>_upgrade_signed.bin` 
    * device_id - when doing a single device update, this will be the device ID that is printed on the serial terminal for the device after it connects and registers with Pelion device management.

## Arguments

* -d _or_ --dryrun
    - Don't run the commands, just print them.
* -u _or_ --multi
    - Use to generate fota manifests that can be used in fota campaigns on multiple devices.  Note that when using this mode, you have to manually start fota update campaigns in the pelion portal, using a filter to target multiple devices.  
* -p _or_ --profile
    - Compile profile.  (Default 'release' for optimal compiled codesize)
* -a _or_ --auto
    - Automatically schedule FOTA operations at a frequency set by --freq
* -f _or_ --freq
    - Number of Fota operations to run per hour if using auto mode (default 5)
* -t _or_ --toolchain
    - The compiler toolchain(s) to run tests with (default is all of these: GCC_ARM, IAR, ARM).  
    - You can provide one or comma-separated list for multiple (-t ARM,GCC_ARM).  
* -m _or_ --mcu
    - The microcontroller to test.  The default is to test all that are connected without having to specify them.  You cannot specify multiple microcontrollers - only a specific one or all (default).

## Running the script
Execute the following command, passing in arguments. The path depends on where you have extracted script.
```
    python ../fota-runner/fota-runner.py
```

## Usage Tips
On Linux, you can create an alias to shorten the command.  Just reference the path to the script.
```
    alias fota="python /home/fota-runner/fota-runner.py"
```

On Windows, you create a similar command alias by creating a batch file called *fota.bat* with the following contents.  Then add the path to the batch file to your PATH environment variable.  This also depends on where you installed the script.
```
    python C:\Users\my_username\Documents\fota-runner\fota-runner.py %*
```

Then run the script from anywhere by typing this on a command line.  
```    
    fota [arguments]
```    
