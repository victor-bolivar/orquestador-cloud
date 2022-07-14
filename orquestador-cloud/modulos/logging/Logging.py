#!/usr/bin/env python3

from datetime import datetime

class Logging():
    def __init__(self) -> None:
        log_file = './orquestador.log'
    
    def log(self, result) -> None:
        date = str(datetime.now())

        if result['valor'] == 3 :
            log_level = 'ERROR'
        elif result['valor'] == 6 :
            log_level = 'INFO'
            
        message = result['mensaje']

        if 'agent' in result:
            agent = result['agent']
        else:
            agent = 'system'

        
        with open("./modulos/logging/orquestador.log", "a") as file_object:
            # Ejemplo de output: 
            # 2022-06-14 16:43:56,238 DEBUG: keystoneauth.session REQ: curl -g -i -X GET http://controller:5000/v3 -H "Accept: application/json" -H "User-Agent: openstacksdk/0.99.0 keystoneauth1/4.6.0 python-requests/2.22.0 CPython/3.8.10"
            line = date +" "+ log_level + ": "+ agent + ": " + message+"\n"
            file_object.write(line)
        
        