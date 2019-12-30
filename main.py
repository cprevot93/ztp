#!/usr/bin/env python3
# -*- coding: utf-8 -*

import sys
import logging
import argparse
import getpass
import time

from read_csv import load_value, read_sn
from ftntlib import FortiManagerJSON
from device import Device

log_level = logging.DEBUG

###############################################
################### MAIN ######################
###############################################
def main():
    log = logging.getLogger('ztp')
    log.setLevel(level=log_level)
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
    sn_list = []
    api = FortiManagerJSON()
    api.login(args.ip, args.user, args.password)
    log.info("> Logging to Fortimanager at {ip}".format(ip=args.ip))

    api.verbose('off')
    api.debug('off')

    # load_value(args.file, device_list)
    read_sn(args.file, sn_list)
    log.info("> There is " + str(len(device_list)) + " devices to import...")
    log.info("> Starting import...\n")
    # for device in device_list:
    #     if device.type == "FGT":
    #         device.add_model_device(api)
    #     if device.type == "FAP":
    #         device.add_fap_to_fmg(api)
    #         continue
    #     if device.type == "FSW":
    #         device.add_fsw_to_fmg(api)
    #         continue

    api.logout()

if __name__ == "__main__":
    main()