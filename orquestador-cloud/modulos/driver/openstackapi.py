#!/usr/bin/env python3

from tabulate import tabulate
import requests
import json
from ..logging.Logging import Logging

class OpenstackApi():
    def __init__(self, OS_USERNAME, OS_PASSWORD, OS_USER_DOMAIN_NAME, OS_PROJECT_DOMAIN_NAME, OS_PROJECT_NAME, OS_AUTH_URL, COMPUTE_URL, NETWORK_URL, GLANCE_URL):
        self.logging = Logging()

        self.OS_USERNAME = OS_USERNAME
        self.OS_PASSWORD = OS_PASSWORD
        self.OS_USER_DOMAIN_NAME = OS_USER_DOMAIN_NAME
        self.OS_PROJECT_DOMAIN_NAME = OS_PROJECT_DOMAIN_NAME
        self.OS_PROJECT_NAME = OS_PROJECT_NAME
        self.OS_AUTH_URL = OS_AUTH_URL
        self.COMPUTE_URL = COMPUTE_URL
        self.NETWORK_URL = NETWORK_URL
        self.GLANCE_URL = GLANCE_URL

        self.TOKEN = None
        self.obtener_token()
    
    def obtener_token(self):
        headers =  {'Content-Type' : 'application/json'}
        url = self.OS_AUTH_URL+"/auth/tokens?nocatalog"
        data = {    "auth":{
                    "identity":{
                        "methods":[
                            "password"
                        ],
                        "password":{
                            "user":{
                                "domain":{
                                    "name":self.OS_USER_DOMAIN_NAME
                                },
                                "name":self.OS_USERNAME,
                                "password":self.OS_PASSWORD
                            }
                        }
                    },
                    "scope":{
                        "project":{
                            "domain":{
                                "name":self.OS_PROJECT_DOMAIN_NAME
                            },
                            "name":self.OS_PROJECT_NAME
                        }
                    }
                }
            }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        self.TOKEN = response.headers['X-Subject-Token']
        self.logging.log({ 'valor': 6, 'agent':'openstackapi', 'mensaje': 'Se obtuvo SATISFACTORIAMENTE el token '+self.TOKEN})

    def crear_keypair(self, nombre, public_key) -> None:
        headers =  { 'Content-Type' : 'application/json',
                     'X-Auth-Token': self.TOKEN} 
        url = self.COMPUTE_URL+"/os-keypairs"
        data = {
            "keypair": {
                "name": nombre,
                "public_key": public_key
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(response.json())

    def obtener_keypairs(self) -> dict:
        headers =  { 'Content-Type' : 'application/json',
                     'X-Auth-Token': self.TOKEN} 
        url = self.COMPUTE_URL+"/os-keypairs"
        response = requests.get(url, headers=headers)
        return response.json()

    def obtener_sg(self):
        headers =  { 'Content-Type' : 'application/json',
                     'X-Auth-Token': self.TOKEN} 
        url = self.NETWORK_URL+"/v2.0/security-groups"
        response = requests.get(url, headers=headers)
        return response.json()['security_groups']

    def crear_sg(self, nombre):
        headers =  { 'Content-Type' : 'application/json',
                     'X-Auth-Token': self.TOKEN} 
        url = self.NETWORK_URL+'/v2.0/security-groups'
        data = {
            "security_group": {
                "name": nombre
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(response.json())

    def crear_sg_rule(self, protocolo, puerto, ip, sg_id):
        headers =  { 'Content-Type' : 'application/json',
                     'X-Auth-Token': self.TOKEN} 
        url = self.NETWORK_URL+"/v2.0/security-group-rules"
        data = {
            "security_group_rule": {
                "direction": "ingress",
                "port_range_min": puerto,
                "ethertype": "IPv4",
                "port_range_max": puerto,
                "protocol": protocolo,
                "remote_ip_prefix": ip,
                "security_group_id": sg_id
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(response.json())

    def crear_red(self, nombre,segmentation_id):
        headers =  { 'Content-Type' : 'application/json',
                     'X-Auth-Token': self.TOKEN} 
        url = self.NETWORK_URL+'/v2.0/networks'
        data = {
            "network": {
                "name": nombre,
                "shared": True,
                "router:external": True,
                "provider:physical_network": "external",
                "provider:network_type": "vlan",
                "provider:segmentation_id": segmentation_id
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(response.json())
        # se devuelve el id de la red creada
        return response.json()['network']['id']
    
    def crear_subred(self, network_id, nombre_subred, cidr):
        headers =  { 'Content-Type' : 'application/json',
                     'X-Auth-Token': self.TOKEN} 
        url = self.NETWORK_URL+'/v2.0/subnets'
        data = {
            "subnet": {
                "name": nombre_subred,
                "ip_version": 4,
                "network_id": network_id,
                "cidr": cidr
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(response.json())

    def listar_flavors(self):
        headers =  { 'Content-Type' : 'application/json',
                     'X-Auth-Token': self.TOKEN} 
        url = self.COMPUTE_URL+"/flavors"
        return requests.get(url, headers=headers).json()['flavors']

    def listar_imagenes(self):
        headers =  { 'Content-Type' : 'application/json',
                     'X-Auth-Token': self.TOKEN} 
        url = self.GLANCE_URL+"/v2/images"
        return requests.get(url, headers=headers).json()['images']
    
    def listar_redes(self):
        headers =  { 'Content-Type' : 'application/json',
                     'X-Auth-Token': self.TOKEN} 
        url = self.NETWORK_URL+"/v2.0/networks"
        return requests.get(url, headers=headers).json()['networks']
    
    def obtener_subred(self, subnet_id):
        headers =  { 'Content-Type' : 'application/json',
                     'X-Auth-Token': self.TOKEN} 
        url = self.NETWORK_URL+'/v2.0/subnets/'+subnet_id
        return requests.get(url, headers=headers).json()['subnet']
    
    def crear_vm(self, nombre, flavor_id, image_id, red_id, keypair, sg_id):
        headers =  { 'Content-Type' : 'application/json',
                     'X-Auth-Token': self.TOKEN} 
        url = self.COMPUTE_URL+'/servers'
        data = {
            "server" : {
                "name" : nombre,
                "flavorRef": flavor_id,
                "imageRef": image_id,
                "networks" : [{
                        "uuid" : red_id
                            }],
                "key_name": keypair,
                "security_groups": [
                    {
                        "name": sg_id
                    }
                ]

            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(response.json())
    
    def listar_vm(self):
        headers =  { 'Content-Type' : 'application/json',
                     'X-Auth-Token': self.TOKEN} 
        url = self.COMPUTE_URL+"/servers"
        return requests.get(url, headers=headers).json()
    
    def obtener_info_vm(self, vm_id):
        headers =  { 'Content-Type' : 'application/json',
                     'X-Auth-Token': self.TOKEN} 
        url = self.COMPUTE_URL+"/servers/"+vm_id
        return requests.get(url, headers=headers).json()

    def obtener_info_flavor(self, flavor_id):
        headers =  { 'Content-Type' : 'application/json',
                     'X-Auth-Token': self.TOKEN} 
        url = self.COMPUTE_URL+"/flavors/"+flavor_id
        return requests.get(url, headers=headers).json()
    
    def obtener_info_imagen(self, image_id):
        headers =  { 'Content-Type' : 'application/json',
                     'X-Auth-Token': self.TOKEN} 
        url = self.GLANCE_URL+"/v2/images/"+image_id
        return requests.get(url, headers=headers).json()

def menu():
    global openstackApi
    while True:
        print('''
            1. Ingresar credenciales
            2. Crear provider network
            3. Crear keypair
            4. Crear o editar grupo de seguridad
            5. Crear VM
            6. Listar VMs
        ''')
        opcion = input('[?] Ingrese su opcion: ')
        print() # imprimir una nueva linea
        if (opcion=='1'):
            openstackApi.OS_USERNAME = input('[?] Ingrese el usuario: ')
            openstackApi.OS_PASSWORD = input('[?] Ingrese la contraseña: ')
            openstackApi.obtener_token()
        elif (opcion=='2'):
            nombre_red = input('[?] Ingrese el nombre de la red: ')
            nombre_subred = input('[?] Ingrese el nombre de la subred: ')
            cidr = input('[?] Ingrese el CIDR: ')
            segmentation_id = input('[?] Ingrese el segmentation ID: ')

            network_id = openstackApi.crear_red(nombre_red, segmentation_id)
            openstackApi.crear_subred(network_id, nombre_subred, cidr)
        elif (opcion=='3'):
            nombre_llave = input('[?] Ingrese el nombre de la llave: ')
            ruta_llave = input('[?] Ingrese la ruta de la llave: ')
            with open(ruta_llave) as f:
                contenido_llave = f.read()
            openstackApi.crear_keypair(nombre_llave, contenido_llave)
        elif (opcion=='4'):
            print('''
            1. Crear grupo de seguridad
            2. Editar grupo de seguridad
            ''')
            opcion = input('[?] Ingrese su opcion: ')
            print() # imprimir una nueva linea
            if (opcion=='2'):
                lista_sg = openstackApi.obtener_sg()
                # 1. se imprime la lista de security groups
                lista_tabular_sg = [ [sg['id'], sg['name']] for sg in lista_sg] # usada para imprimir los datos en una tabla con la libreria 'tabulate'
                print(tabulate(lista_tabular_sg, headers=['id', 'name']), end="\n\n")
                sg_input = input('[?] Ingrese el nombre del SG a editar: ')
                print() # imprimir una nueva linea
                # 2. se impre las reglas dentro del SG
                sg_id = None
                for sg in lista_sg:
                    if sg['name']==sg_input:
                        sg_id = sg['id'] # a usar en la creacion de la regla
                        lista_tabular_rules =  [ [rule['protocol'], rule['port_range_min'], rule['port_range_max'], rule['remote_ip_prefix']] for rule in sg['security_group_rules']]
                        # para que se impriman los valores por defecto
                        for rule in lista_tabular_rules:
                            if rule[0] == None : rule[0] = 'None'
                            if rule[1] == None : rule[1] = 'None'
                            if rule[2] == None : rule[2] = 'None'
                            if rule[3] == None : rule[3] = '0.0.0.0/0'
                        print(tabulate(lista_tabular_rules, headers=['protocol', 'port_range_min', 'port_range_max', 'remote_ip_prefix']), end="\n\n")                        
                        break
                # 2. agregar regla de seguridad
                protocolo = input('[?] Ingrese el protocolo (tcp, udp): ')
                puerto = input('[?] Ingrese el puerto: ')
                ip = input('[?] Ingrese el prefijo de IP remoto: ')
                openstackApi.crear_sg_rule(protocolo, puerto, ip, sg_id)
            elif (opcion=='1'):
                nombre = input('[?] Ingrese el nombre del SG a crear: ')
                openstackApi.crear_sg(nombre)
        elif (opcion=='5'):
            # 0. nombre de la vm
            nombre = input('[?] Ingrese el nombre de la vm: ')
            print()
            # 1. seleccionar flavor
            flavors = openstackApi.listar_flavors()
            lista_tabular_flavors = [ [flavor['id'], flavor['name']] for flavor in flavors] # usada para imprimir los datos en una tabla con la libreria 'tabulate'
            print(tabulate(lista_tabular_flavors, headers=['id', 'name']), end="\n\n")
            flavor_id = input('[?] Ingrese el ID del flavor: ')
            print() # imprimir una nueva linea
            # 2. seleccionar imagen
            imagenes = openstackApi.listar_imagenes()
            lista_tabular_imagenes = [ [imagen['id'], imagen['name']] for imagen in imagenes] # usada para imprimir los datos en una tabla con la libreria 'tabulate'
            print(tabulate(lista_tabular_imagenes, headers=['id', 'name']), end="\n\n")
            imagen_id = input('[?] Ingrese el ID de la imagen: ')
            print() # imprimir una nueva linea
            # 3. seleccionar red
            redes = openstackApi.listar_redes()
            lista_tabular_redes = []
            for red in redes:
                id = red['id']
                name = red['name']
                if red['subnets']:
                    subnet_id = red['subnets'][0]
                    subnet_info = openstackApi.obtener_subred(subnet_id)
                    cidr = subnet_info['cidr']
                else:
                    cidr = '-'
                lista_tabular_redes.append([id, name, cidr]) # usada para imprimir los datos en una tabla con la libreria 'tabulate'
            print(tabulate(lista_tabular_redes, headers=['id', 'name', 'cidr']), end="\n\n")
            red_id = input('[?] Ingrese el ID de la red: ')
            print() # imprimir una nueva linea
            # 4. seleccionar key-pair
            lista_keypair = openstackApi.obtener_keypairs()['keypairs']
            lista_tabular_keypairs = [ [keypair['keypair']['name'], keypair['keypair']['public_key']] for keypair in lista_keypair] # usada para imprimir los datos en una tabla con la libreria 'tabulate'
            print(tabulate(lista_tabular_keypairs, headers=['name', 'public_key']), end="\n\n")
            keypair = input('[?] Ingrese el nombre del keypair: ')
            print() # imprimir una nueva linea
            # 5. seleccionar sg
            lista_sg = openstackApi.obtener_sg()
            lista_tabular_sg = [ [sg['id'], sg['name']] for sg in lista_sg] # usada para imprimir los datos en una tabla con la libreria 'tabulate'
            print(tabulate(lista_tabular_sg, headers=['id', 'name']), end="\n\n")
            sg_id = input('[?] Ingrese el ID del grupo de seguridad: ')
            print() # imprimir una nueva linea
            # 6. se crea la vm
            openstackApi.crear_vm(nombre, flavor_id, imagen_id, red_id, keypair, sg_id)
        elif (opcion=='6'):
            lista_vms = openstackApi.listar_vm()['servers']
            lista_tabular_vm = [ [vm['id'], vm['name']] for vm in lista_vms] # usada para imprimir los datos en una tabla con la libreria 'tabulate'
            print(tabulate(lista_tabular_vm, headers=['id', 'name']), end="\n\n")
            # se obtiene info de una vm en particular
            vm_id = input('[?] Ingrese el ID de la VM para obtener un mayor detalle: ')
            vm_info = openstackApi.obtener_info_vm(vm_id)['server']
            print()
            # 1. nombre
            print(' nombre: '+vm_info['name'])
            # 2. flavor
            flavor_id = vm_info['flavor']['id']
            flavor_info = openstackApi.obtener_info_flavor(flavor_id)['flavor']
            print(' flavor:')
            print('     id: '+vm_info['flavor']['id'])
            print('     nombre: '+flavor_info['name'])
            print('     ram: '+str(flavor_info['ram'])+'mb')
            print('     disk: '+str(flavor_info['disk'])+'gb')
            print('     vcpus: '+str(flavor_info['vcpus']))
            # 3. imagen
            image_id = vm_info['image']['id']
            image_info = openstackApi.obtener_info_imagen(image_id)
            print(' imagen: '+image_info['name'])
            # 4. keyname
            print(' key_name: '+vm_info['key_name'])
            # 5. red, subred e IP
            red = list(vm_info['addresses'].keys())[0]
            direccion_ip = vm_info['addresses'][red][0]['addr']
            print(' red: '+red)
            print(' direccion_ip: '+direccion_ip)
            # 6. grupo de seguridad 
            print(' security_group: '+vm_info['security_groups'][0]['name'])

if __name__ == '__main__':
    openstackApi =  OpenstackApi()
    menu()
    