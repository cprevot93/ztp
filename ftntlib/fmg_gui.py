#!/usr/bin/env python3
# -*- coding: utf-8 -*

###################################################################
#
# File: fmg_gui.py
# Authors: Charles Prevot
# Description: A Python module to automate GUI web interface command for FMG
# Date: 03/01/2020
###################################################################

import time
import logging
import requests
import json
import sys

if sys.version_info >= (2, 7):
    logging.captureWarnings(True)
else:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings()


class FortiManagerGUI (object):

    def __init__(self, ip, verbose=0, timeout=10, ssl_verify=False, stream_log=sys.stdout):
        try:
            self._host = "https://{ip}/".format(ip=str(ip))
            self._user = None
            self._passwd = None

            self._reqid = 1
            self._timeout = int(timeout)
            self._ssl_verify = bool(ssl_verify)
            self._sid = None
            self._http_debug = False
            self._bbcode = False
            self._ws_mode = False
            self._params = False
            self._skip = False
            self._root = False
            self._rootpath = None
            self._csrf_token = None
            self._xsrf_token = None
            self._session = requests.session()

        except Exception as e:
            print("ERROR FortiManagerGUI: " + str(e.args))
            exit(-1)

        self._log = logging.getLogger()
        self.verbose(verbose)

    def jprint(self, json_obj):
        return json.dumps(json_obj, indent=2, sort_keys=True)

    def dprint(self, msg, string):
        if self._bbcode:
            msg = '[color=#008080][b]' + msg + '[/b][/color]'
            string = '[code]' + self.jprint(string) + '[/code]'
        else:
            string = self.jprint(string)
        self._log.debug(msg)
        self._log.debug(string)

    def http_debug(self, status):
        if status == 'on':
            self._http_debug = True
        elif status == 'off':
            self._http_debug = False

    def bbcode(self, status):
        if status == 'on':
            self._bbcode = True
        elif status == 'off':
            self._bbcode = False

    def skip(self, status):
        if status == 'on':
            self._skip = True
        elif status == 'off':
            self._skip = False
        else:
            self._skip = False

    def verbose(self, level):
        if type(level) == int():
            if level == 0:
                self._log.setLevel(None)
            elif level == 1:
                self._log.setLevel(logging.INFO)
            elif level == 2:
                self._log.setLevel(logging.ERROR)
            else:
                self._log.setLevel(logging.DEBUG)
        else:
            self._log.error("verbose must be int")

    def chroot(self, rootpath):
        if rootpath:
            self._root = True
            self._rootpath = rootpath
        else:
            self._root = False

    def params(self, params):
        if params:
            self._params = params

    def timeout(self, timeout):
        if type(timeout) == int():
            self._timeout = timeout

    def login(self, user, passwd):
        url = '{host}/cgi-bin/module/flatui_auth'.format(host=self._host)
        headers = {'content-type': 'application/json'}

        if not self._user: # if none
            self._user = user
            self._passwd = passwd
        else:
            raise Exception("Please logout user {user} before".format(user=self._user))

        body = {
            "id": 1,
            "url": "/gui/userauth",
            "method": "login",
            "params":{
                "username": self._user,
                "secretkey": self._passwd,
                "logintype": 0
            }
        }
        try:
            self._log.debug('REQUEST:\n' + url + '\n' + self.jprint(body))
            response = self._session.post(
                url,
                data=json.dumps(body),
                headers=headers,
                verify=self._ssl_verify,
                timeout=self._timeout
            )
            response_json = response.json()
            self._log.debug('RESPONSE:\n' + self.jprint(response_json))
            if response_json['result'][0]['status']['code'] == 0:
                self._log.debug("Authentication successfull") # Auth failure
            else:
                raise Exception(response_json['result'][0]['status']['message'])

            url = "{host}/p/app/".format(host=self._host)
            self._log.debug('REQUEST:\n' + url + '\n' + self.jprint(body))
            response = self._session.get(
                url,
                verify=self._ssl_verify,
                timeout=self._timeout
            )
            if response.status_code != 200:
                raise Exception("Unknown error during logging")
            self._log.debug('RESPONSE:\n' + response.content.decode('utf-8'))

        except requests.exceptions.ConnectionError:
            raise
        except Exception:
            raise


    def logout(self):
        url = "{host}/p/logout/".format(host=self._host)
        response = requests.get(
            url,
            verify=self._ssl_verify,
            timeout=self._timeout
        )
        if response.status_code == 200:
            self._log.debug("Logout")
            self._user = None
            self._passwd = None
        else:
            self._log.error("Logout failed")
            self._log.debug(response.content)

    def set_auth_headers(self):
        return {
            'X-CSRFToken': self._session.cookies.get('csrftoken'),
            'XSRF-TOKEN': self._session.cookies.get('XSRF-TOKEN'),
            'X-XSRF-TOKEN': "\"" + self._session.cookies.get('XSRF-TOKEN') + "\""
        }

    def get(self, url, timeout=0, verify=None):
        headers = self.set_auth_headers()

        if verify == None:
            verify = self._ssl_verify
        if timeout == 0:
            timeout = self._timeout

        try:
            self._log.debug('REQUEST URL: ' + url)
            response = self._session.get(
                url,
                headers=headers,
                verify=verify,
                timeout=timeout
            )
            response_json = response.json()
            self._log.debug('RESPONSE:\n' + self.jprint(response_json))

        except requests.exceptions.ConnectionError:
            raise
        except Exception:
            raise

    def post(self, url, data, timeout=0, verify=None):
        headers = self.set_auth_headers()
        headers['content-type'] = 'application/json'

        if verify == None:
            verify = self._ssl_verify
        if timeout == 0:
            timeout = self._timeout

        try:
            self._log.debug('REQUEST:\n' + url + '\n' + self.jprint(data))
            response = self._session.post(
                url,
                data=json.dumps(data),
                headers=headers,
                verify=verify,
                timeout=timeout
            )
            response_json = response.json()
            self._log.debug('RESPONSE:\n' + self.jprint(response_json))

        except requests.exceptions.ConnectionError:
            raise
        except Exception:
            raise

        return response.json()


    def exec_script(self, script_id, device_name, adom_id=3):
        url = self._host + "cgi-bin/module/flatui/json"

        data = {
            "id": 2,
            "method":"exec",
            "params":[
                {
                    "url": "deployment/install/script",
                    "data": {
                        "admin": "admin",
                        "adom": adom_id,
                        "host": "0.0.0.0",
                        "iftcl": 0,
                        "scope": [
                            {
                                "name": device_name,
                                "vdom": "global"
                            }
                        ],
                        "ondb": 0,
                        "pkg": 0,
                        "script": int(script_id),
                        "task": 0,
                        "type": "device"
                    }
                }
            ]
        }
        response = self.post(url, data)
        return response['data']['result'][0]['status'], response['data']['result'][0]['data']

