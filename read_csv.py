#!/usr/bin/env python3
# -*- coding: utf-8 -*

import xlrd
import logging
import json

from xlwt import Workbook
from xlutils.copy import copy
from device import Device

log = logging.getLogger()

# check for data integrity, like cluster added by pair
def check_data(device_list):
    for device in device_list:
        # if cluster_id != -1 -> it's a cluster member
        if device.cluster_id != -1:
            second_member_found = False
            # get the serial of the second fgt in csv
            for second_member in device_list:
                if device == second_member:
                    continue
                # if cluster id different -> not the second member of the cluster
                if device.cluster_id != second_member.cluster_id:
                    continue
                second_member_found = True
                device.second_member = second_member
                second_member.second_member = device

    if not second_member_found:
        log.error("CSV data check error.\nCouldn't found second member of cluster group id " + str(device.cluster_id) + "\nExiting...")
        exit(-1)

###############################################
############  Read values csv  ################
###############################################
def load_value(excel_path, device_list):
    # Ouverture du classeur, lecture seule
    classeur = xlrd.open_workbook(excel_path)
    # Récupération du nom de toutes les feuilles sous forme de liste
    nom_des_feuilles = classeur.sheet_names()
    # Récupération de la première feuille
    feuille = classeur.sheet_by_name(nom_des_feuilles[0])
    log.info("Reading device list...")
    try:
        index = dict()
        for i in range(feuille.ncols):
            title = feuille.cell_value(0, i)
            index[str(title).lower()] = i # load a index map named with the title of every column in the CSV LOWERCASE
        log.debug("Excel index mapping:\n" + json.dumps(index, indent=2))
        for i in range(feuille.nrows)[1:]:
            device_list.append(Device())
            device_list[i-1].type = feuille.cell_value(i, index["type"])
            device_list[i-1].sn = feuille.cell_value(i, index["serial"])
            device_list[i-1].model_device = feuille.cell_value(i, index["model_device"])
            device_list[i-1].name = feuille.cell_value(i, index["name"])
            device_list[i-1].adom = feuille.cell_value(i, index["adom"])
            device_list[i-1].vdom = feuille.cell_value(i, index["vdom"])
            device_list[i-1].cluster_id = int(feuille.cell_value(i, index["cluster_id"]))
            if feuille.cell_value(i, index["cluster_pref"]) == "master": device_list[i-1].master = True
            device_list[i-1].enforce_firmware = feuille.cell_value(i, index["enforce_firmware"])
            device_list[i-1].target_firmware = feuille.cell_value(i, index["target_firmware"])
            device_list[i-1].policy_package = feuille.cell_value(i, index["policy_package"])
            device_list[i-1].system_template = feuille.cell_value(i, index["system_template"])
            device_list[i-1].cli_template = feuille.cell_value(i, index["cli_template"])
            device_list[i-1].device_group = feuille.cell_value(i, index["device_group"])
            device_list[i-1].city = feuille.cell_value(i, index["city"])
            device_list[i-1].company = feuille.cell_value(i, index["company"])
            device_list[i-1].contact = feuille.cell_value(i, index["contact"])
            device_list[i-1].country = feuille.cell_value(i, index["country"])
            device_list[i-1].latitude = feuille.cell_value(i, index["latitude"])
            device_list[i-1].longitude = feuille.cell_value(i, index["longitude"])
            device_list[i-1].id_site = int(feuille.cell_value(i, index["id_site"]))
            device_list[i-1].downstream_wan1 = int(feuille.cell_value(i, index["downstream_wan1"]))
            device_list[i-1].downstream_wan2 = int(feuille.cell_value(i, index["downstream_wan2"]))
            device_list[i-1].upstream_wan1 = int(feuille.cell_value(i, index["upstream_wan1"]))
            device_list[i-1].upstream_wan2 = int(feuille.cell_value(i, index["upstream_wan2"]))
            device_list[i-1].sd_wan_template = feuille.cell_value(i, index["sd_wan_template"])
            device_list[i-1].vpn_community = feuille.cell_value(i, index["vpn_community"])
            device_list[i-1].fortiswitch_template = feuille.cell_value(i, index["fortiswitch_template"])
            device_list[i-1].fap_template = feuille.cell_value(i, index["fap_template"])
            device_list[i-1].fgt_name = feuille.cell_value(i, index["fgt_name"])
            device_list[i-1].cli_script = feuille.cell_value(i, index["cli_script"])
            device_list[i-1].sdbranch = feuille.cell_value(i, index["sd_branch"])
            device_list[i-1].platform = feuille.cell_value(i, index["platform"])

        check_data(device_list)

    except IndexError:
        log.error("Error: excel file missing column")

    log.debug(str(len(device_list)) + " devices loaded")