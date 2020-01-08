#!/usr/bin/env python3
# -*- coding: utf-8 -*

import sys
import logging
import argparse
import getpass
import time

from read_csv import load_value
from register_device import wait_and_registered_new_devices
from ftntlib import FortiManagerJSON, FortiManagerGUI
from device import Device

log_level = logging.DEBUG

###############################################
################### MAIN ######################
###############################################
def main():
    log = logging.getLogger()
    logging.basicConfig(stream=sys.stdout, level=log_level)
    log.info("\n\n<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Fortinet SD-WAN Zero Touch Provisionning Tool <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")

    parser = argparse.ArgumentParser(description='ZTP FMG fortinet')
    parser.add_argument('-f', '--file', help='excel file to import data from', required=True)
    parser.add_argument('-i', '--ip', help='Fortimanager IP', required=True)
    parser.add_argument('-u', '--user', help='Fortimanager Username', default="admin")
    parser.add_argument('-p', '--password', help='Fortimanager password')

    args = parser.parse_args()

    if args.password is None:
        try:
            args.password = getpass.getpass()
        except Exception as error:
            log.error(str(error.args))

    device_list = []
    api = FortiManagerJSON()
    api.login(args.ip, args.user, args.password)
    log.info("Logging to Fortimanager at {ip}".format(ip=args.ip))
    api.verbose('off')
    api.debug('on')

    fmg_gui = FortiManagerGUI(args.ip)
    fmg_gui.login(args.user, args.password)

    # read values from CSV
    load_value(args.file, device_list)

    log.info("Starting import...\n")

    # loop to wait for new unauthorized device
    if len(device_list) > 0:
        log.debug(len(device_list))
        wait_and_registered_new_devices(api, fmg_gui, device_list)

    # first loop for model device
    for device in device_list:
        success = True # TODO
        if str(device.model_device).lower() == "yes":
            if device.type == "FGT":
                success = device.add_model_device(api)
            elif device.type == "FAP":
                success = device.add_fap_to_fmg(api)
            elif device.type == "FSW":
                success = device.add_fsw_to_fmg(api)

            if success:
                device_list.remove(device)


    api.logout()

if __name__ == "__main__":
    main()