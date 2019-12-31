#!/usr/bin/env python3
# -*- coding: utf-8 -*

import sys
import logging
import argparse
import getpass
import time

from read_csv import load_value
from register_device import wait_for_devices
from ftntlib import FortiManagerJSON
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

    # read values from CSV
    load_value(args.file, device_list)

    log.info("Starting import...\n")

    # first loop for model device
    for device in device_list:
        success = True # TODO
        if device.type == "FGT":
            if device.model_device == "Yes":
                # device.add_model_device(api)
                if success:
                    device_list.remove(device)
    #     if device.type == "FAP":
    #         device.add_fap_to_fmg(api)
    #         continue
    #     if device.type == "FSW":
    #         device.add_fsw_to_fmg(api)
    #         continue

    if len(device_list) > 0:
        log.debug(len(device_list))
        wait_for_devices(api, device_list)

    api.logout()

if __name__ == "__main__":
    main()