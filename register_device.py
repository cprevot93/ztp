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
        registered_devices = api.get_dev_list(device.adom)
        for reg_dev in registered_devices:
            if reg_dev['sn'] != device.second_member.sn:
                continue
            second_member_found = True
    except Exception as e:
        log.error(str(e.args))

    if not second_member_found:
        log.debug("Second member " + device.second_member.sn + " is not up yet.\nPassing to next device")

    return second_member_found


def set_template(api, device):
    # Assign device to SDWAN Template
    print("Starting Assign " + str(device['name']) + " to SDWAN Template " + str(sdwan))
    status, result = api.assign_sdwantemplate (adom, sdwan, scope)

    # Assign device to CLI Template
    print("Starting Assign " + str(device['name']) + " to CLI Template " + str(clitemplate))
    status, result = api.assign_clitemplate (adom, clitemplate, scope)

    # Assign device to devicegroup
    print("Starting Assign " + str(device['name']) + " to Device Group " + str(devicegroup))
    status, result = api.assign_devicegroup (adom, devicegroup, scope)

    # Install configuration
    print("Starting Install Package " + str(package) + " to Device  " + str(device['name']))
    status, result = api.install_package (adom, package, scope,flags=['install_chg'])

    #status, result = api.update_device_parameters (adom,str(d['name']),param)

    # Define device Location
    print("Starting Define " + str(device['name']) + " parameters ")

    param = {
        "meta fields":  {
            "City":  str(devicelocation[0][1]),
            "Company/Organization":  "Fortinet",
            "Contact":  "yt@fortidavid.fr",
            "Country":  str(devicelocation[0][0]),
            "ID_Site": str(n)
        },
        "name" : str(device['name']) + "-" + str(devicelocation[0][1]).replace(" ", "") + "-" + str(devicelocation[0][2]).replace(" ", ""),
        "location_from": "GUI",
        "desc": str(devicelocation[0][0]) + " - " + str(devicelocation[0][1]) + " - " + str(devicelocation[0][2]),
        "latitude": str(devicelocation[0][3]),
        "longitude": str(devicelocation[0][4])
    }
    status, result = api.update_device_parameters (adom,str(device['name']),param)

    #Change name by FGT-VMXXXX-City-Desc
    device['name'] = str(device['name']) + "-" + str(devicelocation[0][1]).replace(" ", "") + "-" + str(devicelocation[0][2]).replace(" ", "")
    print ("New Name is : " + str(device['name']))

    status, result = api.update_device_parameters(adom, str(device['name']), param)
    status, result = api.install_package (adom, package, scope,flags=['install_chg'])


def wait_for_devices(api, device_list):
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
                            continue

                    # Promote device to the good adom, using csv info
                    log.debug("Adding new device " + str(device.sn) + " to adom " + str(device.adom))
                    status, result = api.register_device(device.adom, unreg_device)

                    if device.cluster_id > -1:
                        # TODO: execute script on master and slave
                        # TODO: remove slave from liste
                        # TODO: change cluster_id to -2 for master
                        pass
                    else:
                        # configuration, templates
                        pass

                    device_list.remove(device)
                    break # device found, don't go thought all the device list
            if is_found:
                break # break second time to update unreg list
            else:
                log.debug("Device " + str(unreg_device["sn"]) + " not found in excel sheet\nPass")

        # condition d'arret
        if len(device_list) > 0:
            time.sleep(15)
        else:
            break