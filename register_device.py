#!/usr/bin/env python3
# -*- coding: utf-8 -*

import sys
import logging
import time
import json

from ftntlib import FortiManagerJSON
from device import Device

log = logging.getLogger()

# check for the mutual present of slave and master
def is_second_member_present(api, device, device_list, unreg_device_list):
    second_member_found = False
    # look for serial of second device in unregistered device
    for unreg_device in unreg_device_list:
        if unreg_device['sn'] != device.second_member.sn:
            continue
        second_member_found = True

    # check in registered device
    try:
        registered_devices = api.get_regis_device(device.adom)
        for reg_dev in registered_devices:
            if reg_dev['sn'] != device.second_member.sn:
                continue
            second_member_found = True
    except Exception as e:
        log.error(str(e.args))

    if not second_member_found:
        log.debug("Second member " + device.second_member.sn + " is not up yet.\nPassing to next device")

    return second_member_found


def is_both_member_registered(api, device):
    second_member_found = False
    # check in registered device
    try:
        registered_devices = api.get_regis_device(device.adom)
        for reg_dev in registered_devices:
            if reg_dev['sn'] != device.second_member.sn:
                continue
            second_member_found = True
    except Exception as e:
        log.error(str(e.args))

    if not second_member_found:
        log.debug("Second member " + device.second_member.sn + " is not registered yet.")

    return second_member_found


def push_conf(api, device):
    if device.cli_template != "":
        device.assign_cli_template(api)
    if device.policy_package != "":
        device.assign_policy_package(api)
    if device.device_group != "":
        device.assign_device_group(api)
    if device.system_template:
        device.assign_system_template(api)
    # device.interface_mapping(api)
    # device.address_mapping(api, "NET-LAN")
    if device.sdbranch == "yes":
        device.address_mapping(api, "NET-CORP")
    device.install_config(api)
    if device.sd_wan_template != "":
        device.assign_sdwan_template(api)
        device.install_config(api)

def push_ha_conf(api, device, device_list):
    script_name = "slave"
    if device.master:
        script_name = "master"
        device.cluster_id = -2
        device_list.append(device) # add master to the list of expected unregistered fgt
    status, response = api.exec_script(device.adom, device.name, device.vdom, script_name, timeout=60)

    if status['code'] == -1: # timeout
        log.debug(status['message'])
        status, response = api.delete_task(response)
        # if not device.master: # delete only the slave
        status, response = api.delete_device(device.adom, device.name, wait=False)


def wait_and_registered_new_devices(api, device_list):
    while(True):
        status, unreg_device_list = api.get_unreg_devices()

        if not unreg_device_list:
            log.info("No new device, waiting...")
        for unreg_device in unreg_device_list:
            log.debug("New unregistered device " + str(unreg_device['name']))
            is_found = False
            for device in device_list:
                if unreg_device['sn'] == device.sn:
                    is_found = True
                    # check if the device needs to be a cluster
                    if device.cluster_id > -1:
                        if not is_second_member_present(api, device, device_list, unreg_device_list):
                            # wait for second member
                            break

                    # Promote device to the good adom, using csv info
                    log.debug("Adding new device " + str(device.sn) + " to adom " + str(device.adom))
                    status, result = api.register_device(device.adom, unreg_device, device.name)

                    device_list.remove(device)
                    if device.cluster_id < 0: # normal device or master configured
                        # check state cluster
                        # if device.cluster_id == -2 and unreg_device['ha_mode'] == 0:
                        #     log.error("Something when wrong with cluster formation")
                        #     exit(-1)
                        # push configurations & templates
                        push_conf(api, device)
                    elif is_both_member_registered(api, device):
                        # slave or master not configured
                        # push HA conf with script
                        if not device.master:
                            # master first
                            device = device.second_member

                        # time.sleep(10)
                        push_ha_conf(api, device, device_list)
                        # time.sleep(10)
                        push_ha_conf(api, device.second_member, device_list)

                    break # device found, don't go thought all the device list
            if is_found:
                break # break second time to update unreg device list
            else:
                log.debug("Device " + str(unreg_device["sn"]) + " not found in excel sheet\nPass")

        # condition d'arret
        if len(device_list) > 0:
            time.sleep(15)
        else:
            break