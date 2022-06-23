#!/usr/bin/env python3


class Logging():
    def __init__(self) -> None:
        log_file = './orquestador.log'
    
    def log(self, result) -> None:
        # TODO escribir al archivo
        date = None
        log_level = None
        agent = 'linuxcluster'
        message = None
        # 2022-06-14 16:43:56,238 DEBUG: keystoneauth.session REQ: curl -g -i -X GET http://controller:5000/v3 -H "Accept: application/json" -H "User-Agent: openstacksdk/0.99.0 keystoneauth1/4.6.0 python-requests/2.22.0 CPython/3.8.10"
        pass