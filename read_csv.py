#!/usr/bin/env python3
# -*- coding: utf-8 -*

import xlrd
import logging

from xlwt import Workbook
from xlutils.copy import copy
from device import Device

log = logging.getLogger('ztp')

def read_sn(excel_path, sn_list):
    # Ouverture du classeur, lecture seule
    classeur = xlrd.open_workbook(excel_path)
    # Récupération du nom de toutes les feuilles sous forme de liste
    nom_des_feuilles = classeur.sheet_names()
    # Récupération de la première feuille
    feuille = classeur.sheet_by_name(nom_des_feuilles[0])
    log.info("> Reading all SN...")
    try:
        i = 0
        for j in range(feuille.ncols):
            title = feuille.cell_value(0, j)
            if title == "Device_SN":
                i = j
                break
        for k in range(feuille.nrows)[1:]:
            serial = feuille.cell_value(k, i)
            log.info(str(serial))
            sn_list.append(serial)

    except IndexError:
        print("Error: excel file missing column")

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
    print("> Reading device list...")
    try:
        for i in range(feuille.nrows)[1:]:
            device_list.append(Device())
            device_list[i-1].type = feuille.cell_value(i, 0)
            device_list[i-1].sn = feuille.cell_value(i, 1)
            device_list[i-1].name = feuille.cell_value(i, 2)
            device_list[i-1].enforce_firmware = feuille.cell_value(i, 3)
            device_list[i-1].target_firmware = feuille.cell_value(i, 4)
            device_list[i-1].policy_package = feuille.cell_value(i, 5)
            device_list[i-1].system_template = feuille.cell_value(i, 6)
            device_list[i-1].cli_template = feuille.cell_value(i, 7)
            device_list[i-1].device_group = feuille.cell_value(i, 8)
            device_list[i-1].city = feuille.cell_value(i, 9)
            device_list[i-1].company = feuille.cell_value(i, 10)
            device_list[i-1].contact = feuille.cell_value(i, 11)
            device_list[i-1].country = feuille.cell_value(i, 12)
            device_list[i-1].latitude = feuille.cell_value(i, 13)
            device_list[i-1].longitude = feuille.cell_value(i, 14)
            device_list[i-1].id_site = int(feuille.cell_value(i, 15))
            device_list[i-1].downstream_wan1 = int(feuille.cell_value(i, 16))
            device_list[i-1].downstream_wan2 = int(feuille.cell_value(i, 17))
            device_list[i-1].upstream_wan1 = int(feuille.cell_value(i, 18))
            device_list[i-1].upstream_wan2 = int(feuille.cell_value(i, 19))
            device_list[i-1].sd_wan_template = feuille.cell_value(i, 20)
            device_list[i-1].vpn_community = feuille.cell_value(i, 21)
            device_list[i-1].fortiswitch_template = feuille.cell_value(i, 22)
            device_list[i-1].fap_template = feuille.cell_value(i, 23)
            device_list[i-1].adom = feuille.cell_value(i, 24)
            device_list[i-1].vdom = feuille.cell_value(i, 25)
            device_list[i-1].fgt_name = feuille.cell_value(i, 26)
            device_list[i-1].cli_script = feuille.cell_value(i, 27)
            device_list[i-1].sdbranch = feuille.cell_value(i, 28)
            device_list[i-1].platform = feuille.cell_value(i, 29)
            #print(device_list[i-1].print())
    except IndexError:
        print("Error: excel file missing column")
    #print(str(len(device_list)) + " devices importés")