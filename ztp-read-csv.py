#!/usr/bin/env python3
# -*- coding: utf-8 -*

import sys
import xlrd
import logging
import argparse
import getpass
import json 
import time

from xlwt import Workbook
from xlutils.copy import copy
from ftntlib import FortiManagerJSON
from device import Device

logger = None
###############################################
############  Read values csv  ################
###############################################
def readvalue(excel_path, device_list): 
  # Ouverture du classeur, lecture seule
  classeur = xlrd.open_workbook(excel_path)
  # Récupération du nom de toutes les feuilles sous forme de liste
  nom_des_feuilles = classeur.sheet_names()
  # Récupération de la première feuille
  feuille = classeur.sheet_by_name(nom_des_feuilles[0])
  print(u"> Lecture des devices à importer...")
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
      #print(device_list[i-1].print())
  except IndexError:
    print("Error: excel file missing column")
  #print(str(len(device_list)) + " devices importés")

###############################################
######### Add model device to FMG #############
###############################################
def add_model_device(api, device):
  url = "/dvmdb/adom/{}/device/{}".format(device.adom, device.name)
  status, response = api.get(url)
  # print_response(status, response)
  # si la réponse de la requete échoue, le FortiGate n'existe PROBABLEMENT pas (cf autre erreur ?)
  if status['code'] == 0:
      print(">> {} already exist".format(device.name))
      return

  print(u">> Add Device Model for : " + device.name)
  url = 'dvm/cmd/add/device' 

  json_device={}
  json_device['mgmt_mode'] = "fmg"
  json_device['device action'] = "add_model"
  json_device['mr'] = "2"
  json_device['os_type'] = "fos"
  json_device['os_ver'] = "6.0"
  json_device['branch_pt'] = "1005"
  json_device['name'] = device.name
  json_device['sn'] = device.sn
  json_device['latitude'] = str(device.latitude)
  json_device['longitude'] = str(device.longitude)

  meta_fields = {}
  meta_fields['Contact Email'] = device.contact
  meta_fields['Country'] = device.country
  meta_fields['City'] = device.city
  meta_fields['Site_Name'] = device.name
  meta_fields['ID_SITE'] = str(device.id_site)
  meta_fields['downstream-wan1'] = str(device.downstream_wan1)
  meta_fields['downstream-wan2'] = str(device.downstream_wan2)
  meta_fields['upstream-wan1'] = str(device.upstream_wan1)
  meta_fields['upstream-wan2'] = str(device.upstream_wan2)

  json_device['meta fields'] = meta_fields

  data = {
    'adom' : device.adom,
    'device' : json_device,
    'flags' : [ 'create_task' , 'nonblocking' ]
  }

  status, response = api._do('exec', url, data)
  #print(json.dumps(data, indent=4))
  #print(json.dumps(response, indent=4))
  if response['taskid']:
    status, response = api.taskwait(response['taskid'])
  else:
    return status, response
  #print(str(status) + "\n" + json.dumps(response, indent=2))
  if response['line'][0]['err'] != 0:
    print("Error: add device fail")
    return False
  
  ucode, ures = api.update_device(device.adom, device.name)
  if ucode !=0:
    return ucode, ures
  rcode, rres = api.reload_devlist(device.adom, {'name' : device.name}, 'dvm')
  if rcode !=0:
    return rcode, rres   
  return

###############################################
################### MAIN ######################
###############################################
def main():
  global logger

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
      print('ERROR', error)

  # logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
  # logger = logging.getLogger()

  device_list = []
  api = FortiManagerJSON()
  api.login(args.ip, args.user, args.password)
  api.verbose('off')
  api.debug('off')
  readvalue(args.file, device_list)
  print(u"> Il y a " + str(len(device_list)) + " devices à importer...")
  print(u"> Debut de l'import...")
  for device in device_list:
    if device.type == "FGT":
      if add_model_device(api, device):
        device.link_device(api)
        device.execute_cli_script(api)
        device.assign_cli_template(api)
        device.assign_policy_package(api)
        device.assign_device_group(api)
        device.assign_system_template(api)
        device.interface_mapping(api)
        device.address_mapping(api)
        device.install_config(api)
        time.sleep(5)
        device.assign_sdwan_template(api)
        device.install_config(api)
        time.sleep(5)
        continue
    if device.type == "FAP":
      device.add_fap_to_fmg(api)
      continue
    if device.type == "FSW":
      device.add_fsw_to_fmg(api)
      continue
  for device in device_list:
    if device.type == "FGT":
      device.install_config(api)
      time.sleep(5)
      continue
  
  api.logout()

if __name__ == "__main__":
    main()