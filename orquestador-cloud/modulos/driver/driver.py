#!/usr/bin/env python3

from nis import cat
from syslog import syslog
from prettytable import PrettyTable
import pandas as pd
import json
import csv

from .ssh import SSH
from .db import DB

from ..config.crendentials import config_controller_lc
from ..config.crendentials import config_db_linuxcluster
from ..config.crendentials import config_w1_lc
from ..config.crendentials import config_w2_lc
from ..config.crendentials import config_w3_lc

from ..config.crendentials import config_openstack
from ..config.crendentials import config_db_openstack

import openstack
openstack.enable_logging(debug=True, path='./modulos/logging/orquestador.log')


class Driver():
    def __init__(self) -> None:
        # Arquitectura#1 : Linux Cluster
        self.linuxc_db = DB(config_db_linuxcluster['host'],
                            config_db_linuxcluster['username'],
                            config_db_linuxcluster['password'],
                            config_db_linuxcluster['database'])
        self.linuxc_controller = SSH(config_controller_lc['host'],
                                     config_controller_lc['port'],
                                     config_controller_lc['username'],
                                     config_controller_lc['private_key'],
                                     config_controller_lc['passphrase'])
        self.linuxc_worker1 = SSH(config_w1_lc['host'],
                                     config_w1_lc['port'],
                                     config_w1_lc['username'],
                                     config_w1_lc['private_key'],
                                     config_w1_lc['passphrase'])
        self.linuxc_worker2 = SSH(config_w2_lc['host'],
                                     config_w2_lc['port'],
                                     config_w2_lc['username'],
                                     config_w2_lc['private_key'],
                                     config_w2_lc['passphrase'])
        self.linuxc_worker3 = SSH(config_w3_lc['host'],
                                     config_w3_lc['port'],
                                     config_w3_lc['username'],
                                     config_w3_lc['private_key'],
                                     config_w3_lc['passphrase'])
        self.linuxc_ofs = None
        # Arquitectura#2 : OpenStack
        self.openstacksdk = openstack.connect(
                                auth_url=config_openstack['auth_url'],
                                project_name=config_openstack['project_name'],
                                username=config_openstack['username'],
                                password=config_openstack['password'],
                                user_domain_name=config_openstack['user_domain_name'],
                                project_domain_name=config_openstack['project_domain_name'])
        self.openstack_db = DB(config_db_openstack['host'],
                            config_db_openstack['username'],
                            config_db_openstack['password'],
                            config_db_openstack['database'])

    # Linux Cluster: Scheduler

    def filter(self, vm: dict, az: list) -> list:
        '''
            inputs
            ---
            vm:  
                    {
                        "n_vcpus": 2,
                        "memoria": 2,
                        "filesystem": {
                            "filesystem": "CopyOnWrite"
                        },
                        "imagen_id": 1,
                        "internet": true
                    }
            
            az: 
                ["1", "2"]

            outputs:
            ---
            workers_filter: 
                [{'idWorker': 1, 'hostname': 'worker1', 'vcpuLibres': '2', 'memoriaLibre': '70', 'discoLibre': '30', 'vcpu': '3', 'memoria': '16', 'disco': '50'}, 
                {'idWorker': 2, 'hostname': 'worker2', 'vcpuLibres': '3', 'memoriaLibre': '50', 'discoLibre': '50', 'vcpu': '3', 'memoria': '16', 'disco': '50'}]

        '''
        workers_db = self.linuxc_db.obtener_workers() 
        workers_az = [] # lista con los workers que pertenecen al AZ
        for worker in workers_db:
            if (str(worker['idWorker']) in az):
                workers_az.append(worker)
        workers_filter = [] # donde se almacenara la info de los workers que cuentan con recursos suficientes
        for worker in workers_az:
                if ( (int(worker['vcpuLibres'])>=vm['n_vcpus']) and (int(worker['memoriaLibre'])>=vm['memoria']) and (int(worker['discoLibre'])>=vm['filesystem']['size'])):
                    # y se añade a la lista de workers con recursos suficientes
                    workers_filter.append(worker)
        return workers_filter

    def cpu_exponential_weigted_average(self, data) -> float:
        '''
            Se devuelve el uso promedio (%) calculado en base a Exponential Moving Average,
            lo que le da mas peso a las ultima metricas

            https://www.geeksforgeeks.org/how-to-calculate-an-exponential-moving-average-in-python/

            inputs
            ---
            data: lista con los usos (ex:[80,60,50,20])

            output
            ---
            cpu_usage: valor de 0 a 1
        '''
        # create a dataframe
        cpu_metrics = pd.DataFrame({'cpu_usage': data})
        # finding EMA
        ema = cpu_metrics.ewm(alpha=0.5).mean()
        return float(ema["cpu_usage"].iloc[-1])/100

    def scheduler(self, workers) -> dict:
        '''
            Funcion que recibe como argumento la lista de disccionarios con 
            informacion de cada worker dentro del AZ con el fin de calcular 
            el coeficiente de carga.

            Este coeficiente se calcula bajo la siguiente formula:
                coeficiente_carga = (cpu_reservados/cpu_total)*0.1 + cpu_avg*0.9
            
            Una vez calculado, se define el worker mas optimo (menor coeficiente)
            y se devuelve un diccionario con la informacion de este.

            input
            ---
            workers(list): informacion obtenida de la base de datos
                 [
                    {'idWorker': 1, 'hostname': 'worker1', 'vcpuLibres': '2', 'memoriaLibre': '70', 'discoLibre': '30', 'vcpu': '3', 'memoria': '16', 'disco': '50'},
                    {'idWorker': 2, 'hostname': 'worker2', 'vcpuLibres': '3', 'memoriaLibre': '50', 'discoLibre': '50', 'vcpu': '3', 'memoria': '16', 'disco': '50'},
                    {'idWorker': 3, 'hostname': 'worker3', 'vcpuLibres': '2', 'memoriaLibre': '40', 'discoLibre': '50', 'vcpu': '5', 'memoria': '32', 'disco': '80'}
                ]
            
            output
            ---
            worker_asignado(dict):
                    {'idWorker': 1, 'hostname': 'worker1', 'vcpuLibres': '2', 'memoriaLibre': '70', 'discoLibre': '30', 'vcpu': '3', 'memoria': '16', 'disco': '50', 'coef':0.43059895833333334},


        '''
        #   Primero, se calcula el COEFICIENTE DE CARGA para cada worker
        for worker in workers:
            # 1. cpu_avg -> se obtiene el uso promedio del CPU (%) 
            if worker['hostname'] == 'worker1':
                list_cpu_usage = self.linuxc_worker1.list_cpu_usage('/home/w1/worker1_cpu_metrics')
                cpu_avg = self.cpu_exponential_weigted_average(list_cpu_usage)  # exponential weigted average
            elif worker['hostname'] == 'worker2':
                # Worker 2
                list_cpu_usage = self.linuxc_worker2.list_cpu_usage('/home/w2/worker2_cpu_metrics')
                cpu_avg = self.cpu_exponential_weigted_average(list_cpu_usage)  # exponential weigted average
            elif worker['hostname'] == 'worker3':
                # Worker 3
                list_cpu_usage = self.linuxc_worker3.list_cpu_usage('/home/wk3/worker3_cpu_metrics')
                cpu_avg = self.cpu_exponential_weigted_average(list_cpu_usage)  # exponential weigted average
            # 2. se obtiene la cantidad de CPU libre
            cpu_reservados = int(worker['vcpu']) - int(worker['vcpuLibres'])
            cpu_total = int(worker['vcpu'])
            # 3. se calcula el coeficiente de carga
            worker['coef'] = (cpu_reservados/cpu_total)*0.1 + cpu_avg*0.9
        # Ahora, se obtiene el worker con el menor coeficiente de carga
        return min(workers, key=lambda x:x['coef'])

    def crear_topologia(self, nueva_topologia) -> dict:
        if (nueva_topologia['infraestructura']['infraestructura'] == "Linux Cluster"):
            # se obtiene los ID de los workers dentro de la AZ
            az = nueva_topologia['infraestructura']['az']
            # se analiza para cada VM
            for vm in nueva_topologia['vms']:
                # 1. filter
                workers = self.filter(vm, az)
                # 2. obtener worker asignado
                worker_asignado = self.scheduler(workers)

                break # solo vm1 por ahora
            

        elif (nueva_topologia['infraestructura']['infraestructura'] == "OpenStack"):
            pass



        print('[+] Se creó correctamente')
        result = {
            'valor': 6,
            'mensaje': 'Topologia creada correctamente'
        }
        return result

    def recursos_suficientes_topologia(self, nueva_topologia) -> bool:
        '''
            Dada la informacion ingresada por el usuario, se verifica que existan los recursos suficientes 
            haciendo la consulta a la DB de la infraestructura correspondiente.

            De ser asi, se se retorna un 'True'. 
            Sino, se retorna un 'False' indicando que no existen los recursos suficientes.

            inputs
            ---
                nueva_topologia (dict): diccionario que almacena la informacion de la topologia a separar.
            
            outputs
            ---
                recursos_suficientes (bool): booleano que indica si existen los recursos sufientes.
            
        '''

        if (nueva_topologia['infraestructura']['infraestructura'] == "Linux Cluster"):
            recursos_suficientes = None
            # se obtiene los ID de los workers dentro de la AZ
            az = nueva_topologia['infraestructura']['az']
            workers_db = self.linuxc_db.obtener_workers()
            # se obtiene una lista con la informacion de los workers dentro del AZ
            workers_validos = [] 
            for worker in workers_db:
                if (str(worker['idWorker']) in az):
                    workers_validos.append(worker)
            # se itera sobre cada vm para verificar si hay recursos suficientes
            for vm in nueva_topologia['vms']:
                if (recursos_suficientes != False):
                    # si recursos_suficientes = False, significa que para una VM no hay recursos suficientes, por lo que la topologia dejaria de ser valida
                    for worker in workers_validos:
                        if ( (int(worker['vcpuLibres'])>=vm['n_vcpus']) and (int(worker['memoriaLibre'])>=vm['memoria']) and (int(worker['discoLibre'])>=vm['filesystem']['size'])):
                            # si hay recursos suficientes, se van restando para no considerarlos al evaluar las demas VMs
                            worker['vcpuLibres'] = int(worker['vcpuLibres']) - vm['n_vcpus']
                            worker['memoriaLibre'] = int(worker['memoriaLibre']) - vm['memoria']
                            worker['discoLibre'] = int(worker['discoLibre']) - vm['filesystem']['size']
                            recursos_suficientes = True
                            break
                        else:
                            recursos_suficientes = False
                            if (worker == workers_validos[-1]):
                                # si es el ultimo worker y no hay recursos suficientes, entonces no hay espacio en todo el slice
                                break
            return recursos_suficientes
        # TODO caso openstack

    # Funciones completadas

    def listar_topologias(self) -> None:
        # obtener data de la db
        linuxc_db = self.linuxc_db.obtener_topologias()
        openstack_db = self.openstack_db.obtener_topologias()
        # armar tabla
        x = PrettyTable()
        x.field_names = ["ID", "Nombre", "Tipo", "Infraestructura"]
        for row in linuxc_db:
            x.add_row([row['idTopologia'], row['nombre'], row['tipo'], 'Linux Cluster'])
        for row in openstack_db:
            x.add_row([row['idTopologia'], row['nombre'], row['tipo'], 'OpenStack'])
        # Espaciado antes de imprimar la tabla
        x = '\n' + str(x)
        x = x.replace("\n", "\n                ")
        print(x)
    
    def listar_imagenes(self) -> None:
        '''
            Funcion que imprime una tabla con las imagenes disponibles
        '''
        print(self.obtener_imagenes())

    def obtener_imagenes(self) -> str:
        '''
            Funcion que devuelve una tabla con las imagenes disponibles
        '''
        imagenes = self.linuxc_db.get('select * from Imagen order by categoria desc;')

        # se arma la tabla
        t = PrettyTable()
        t.field_names = ["ID", "Tipo de imagen", "Nombre", "Ultimo uso"]
        for imagen in imagenes:
            t.add_row([imagen["idImagen"], imagen["categoria"], imagen["nombre"], imagen["fechaUltimoUso"]])
        t = str(t)
        t = '                '+str(t)
        t = t.replace("\n", "\n                ")
        return t

    # Funciones en desarrollo

    def importar_imagen(self, data) -> dict:
        if (data['opcion'] == 1):
            # Subir archivo local
            # 1. Linux Cluster
            #self.linuxc_controller.subir_archivo(data['ruta'], '/home/grupo2/imagenes/'+data['categoria']+'/'+data['nombre'])
            # TODO actualizar db
            # TODO usar sdk para openstack
            print('\n[+] Imagen importada correctamente')
        elif(data['opcion'] == 2):
            # Subir desde URL
            # 1. Linux Cluster
            #self.linuxc_controller.ejecutar_comando('wget '+data['url']+' -O /home/grupo2/imagenes/'+data['categoria']+'/'+data['nombre'])
            # TODO actualizar db
            # TODO usar sdk para openstack
            print('\n[+] Imagen importada correctamente')
        return {
            'valor': 6,
            'mensaje': 'Imagen importada correctamente'
        }

    def topologia_json(self, topology_id) -> None:
        if topology_id < 1000:
            # si el ID de la topologia es < 1000, se trata de una topologia en Linux Cluster
            topologia = self.linuxc_db.get('select * from Topologia where idTopologia=%s', topology_id)[0]
            az = self.linuxc_db.get('SELECT * FROM Topologia_has_Worker tw  INNER JOIN Worker w ON w.idWorker = tw.Worker_idWorker INNER JOIN Topologia t ON t.idTopologia = tw.Topologia_idTopologia where Topologia_idTopologia=%s', topology_id)
            vlans = self.linuxc_db.get('select * from Vlan where Topologia_idTopologia=%s', topology_id)
            # vms e interfaces
            vms = self.linuxc_db.get('select * from VM where Topologia_idTopologia=%s', topology_id)
            vm_parsed = []
            for vm in vms:
                # parsear el nombre de la imagen
                imagen_id = vm["Imagen_idImagen"]
                imagen_nombre = self.linuxc_db.get('select * from Imagen where idImagen=%s', imagen_id)[0]['nombre']
                # parsear las interfaces
                vm_id = vm["idVM"]
                interfaces = self.linuxc_db.get('select * from Interfaz where VM_idVM=%s', vm_id)
                interfaces_parsed = []
                for interfaz in interfaces:
                    interfaces_parsed.append({
                        "id": interfaz['idInterfaz'],
                        "vlanID": interfaz['Vlan_idVlan'],
                        "direccion_ip": interfaz['direccionIP'],
                        "conexionInternet": True if (int(interfaz['internet'])==1) else False,
                        "nombre": interfaz['nombre']
                        
                    })
                # parseo final de vm
                vm_parsed.append({
                    "id": vm["idVM"],
                    "nombre": vm["nombre"],
                    "imagen": imagen_nombre,
                    "vcpu": int(vm["vCPU"]),
                    "memoria": int(vm["memoria"]),
                    "filesystem": vm["tipoFilesystem"],
                    "disco": int(vm["tamaño"]),
                    "interfaces": interfaces_parsed
                })

        elif topology_id < 2000:
            # TODO OpenStack
            pass

        # se parsean las workers en el az
        az_parsed = []
        for worker in az:
            az_parsed.append({
                    "idWorker": worker['Worker_idWorker'],
                    "hostname": worker['hostname'],
                    "cpuLibres": int(worker['vcpuLibres']),
                    "memoriaLibre": int(worker['memoriaLibre']),
                    "discoLibre": int(worker['discoLibre']),
                    "cpuTotales": int(worker['vcpu']),
                    "memoriaTotal": int(worker['memoria']),
                    "discoTotal": int(worker['disco']),
            })
        # se parsean las vlans
        vlans_parsed = []
        for vlan in vlans:
            vlans_parsed.append({
                "id": vlan['idVlan'],
                "gateway": vlan["gateway"],
                "dhcpServer": vlan["dhcpServer"],
                "network": vlan["network"]
        })
        # parseo final
        topologia_json = {
                "id": topologia['idTopologia'],
                "nombre": topologia["nombre"], 
                "tipo": topologia["tipo"],
                "infraestructura": "Linux Cluster",
                "az": az_parsed,
                "vlans": vlans_parsed,
                "vms": vm_parsed
        }
        topologia_json = json.dumps(topologia_json, indent=4)
        topologia_json = '\n' + str(topologia_json)
        topologia_json = topologia_json.replace("\n", "\n                ")
        print(topologia_json)
        
    def topologia_visualizador(self, topology_id) -> None:
        if topology_id < 1000:
            # si el ID de la topologia es < 1000, se trata de una topologia en Linux Cluster
            # vms e interfaces
            vms = self.linuxc_db.get('select * from VM where Topologia_idTopologia=%s', topology_id)
            vm_parsed = []
            enlaces_parsed = []
            for vm in vms:
                # parsear el nombre de la imagen
                imagen_id = vm["Imagen_idImagen"]
                # icono a usar dependiendo de la categoria
                categoria_imagen = self.linuxc_db.get('select * from Imagen where idImagen=%s', imagen_id)[0]['categoria']
                icon = ''
                if categoria_imagen == 'seguridad': # TODO cambiar por Seguridad
                    icon = 'firewall'
                elif categoria_imagen == 'Networking':
                    icon = 'router'
                elif categoria_imagen == 'Server':
                    icon = 'server'
                # se añade
                vm_parsed.append({
                    "id": vm["idVM"],
                    "name": vm["nombre"],
                    "icon": icon,
                })

                # parsear las enlaces
                vm_id = vm["idVM"]
                interfaces = self.linuxc_db.get('select * from Interfaz where VM_idVM=%s', vm_id)
                for interfaz in interfaces:
                    # se evalua el target
                    target_id = interfaz['target'] 
                    if target_id == -1:
                        tgt_device = 'Bus'
                        tgt_ifname = ''
                        tgt_icon = 'cloud'
                    elif target_id <= -2:
                        tgt_device = 'SW'
                        tgt_ifname = '' # TODO evaluar si se puede colocar el puerto de la unterfaz del switch
                        tgt_icon = 'switch'
                    else:
                        # TODO se hace otra consulta a la db (target_id = id de la otra interfaz a la cual se conecta)
                        tgt_device = 'PC90'
                        tgt_ifname = 'en8'
                        tgt_icon = 'server'
                        
                    # se arma el json del enlace
                    enlaces_parsed.append({
                        "source": int(vm_id),
                        "srcDevice": vm["nombre"],
                        "srcIfName": interfaz['nombre'],

                        "target": target_id,
                        "tgtDevice": tgt_device,
                        "tgtIfName": tgt_ifname,
                    })

        elif topology_id < 2000:
            # TODO OpenStack
            pass
        
        # se hace una verificacion, si se usa un bus (topologia lineal) o switch (topologia arbol) 
        # para que se visualize se debe añadir a la lista de vm_parsed
        for enlace in enlaces_parsed:
            if enlace['target'] == -1:
                vm_parsed.append({
                    "id": -1,
                    "name": "Bus",
                    "icon": "cloud",
                })
                break
            if enlace['target'] <= -2: # en topologia arbol hay +1 switch, entonces cada switch tendria un ID negativo a partir de -2
                vm_parsed.append({
                    "id": enlace['target'],
                    "name": "SW",
                    "icon": "switch",
                })
                break

        # opciones "icon": unknown, switch, router, server, phone, host, cloud, firewall
        # target = -1 (bus / icono:cloud)
        # target = -2 (switch)
        # categoria = server (icono:server)
        # categoria = networking (icono:router)
        # categoria = segiridad (icono:firewall)
        topologia_json_visualizador = {
            "nodes": vm_parsed,
            "links": enlaces_parsed
        }
        print(topologia_json_visualizador)
        return topologia_json_visualizador

    def workers_info(self) -> dict:
        '''
            output
            ---
            workers_info:   se devuelve un diccionario con la informacion de los workers dentro de cada infraestructura
                            con el fin de que el usuario defina su AZ en el modulo validador

                            {
                                'openstack': tabla_openstack,
                                'linux_cluster': tabla_lc,
                            }

        '''
        # 1. tabla_openstack
        tabla_openstack = PrettyTable()
        tabla_openstack.field_names = ["ID", "Nombre", "Porcentaje de uso de CPU", "cantidad disponible de vCPU",
                                       "cantidad de memoria libre", "cantidad de disco libre"]
        tabla_openstack.add_row(
            ["1001", "Worker1", "30 %", 16, "3 GB", "20 GB"])
        tabla_openstack.add_row(
            ["1002", "Worker2", " 50 %", 10, "2 GB", "15 GB"])
        tabla_openstack.add_row(
            ["1003", "Worker3", " 60 %", 12, "2 GB", "10 GB"])
        tabla_openstack = str(tabla_openstack)
        tabla_openstack = '                '+tabla_openstack
        tabla_openstack = tabla_openstack.replace("\n", "\n                ")
        # 2. tabla_lc
        tabla_lc = PrettyTable()
        tabla_lc.field_names = ["ID", "Nombre", "Porcentaje de uso de CPU", "cantidad disponible de vCPU",
                                "cantidad de memoria libre", "cantidad de disco libre"]
        tabla_lc.add_row(["1", "Worker1", "30 %", 16, "3 GB", "20 GB"])
        tabla_lc.add_row(["2", "Worker2", " 50 %", 10, "2 GB", "15 GB"])
        tabla_lc.add_row(["3", "Worker3", " 60 %", 12, "2 GB", "10 GB"])
        tabla_lc = str(tabla_lc)
        tabla_lc = '                '+tabla_lc
        tabla_lc = tabla_lc.replace("\n", "\n                ")

        return {
            'openstack': tabla_openstack,
            'linux_cluster': tabla_lc
        }

    # Funciones pendientes
    
    def separar_recursos_nodo(self, nuevo_nodo) -> list:
        '''
            Dada la informacion ingresada por el usuario, se verifica que existan los recursos suficientes 
            haciendo la consulta a la DB de la infraestructura correspondiente.

            De ser asi, se procederia a separar los recursos y se retorna un 'True'. 
            Sino, se retorna un 'False' indicando que no existen los recursos suficientes.

            inputs
            ---
                nuevo_nodo (dict): diccionario que almacena la informacion del nodo a separar.
            
            outputs
            ---
                recursos_suficientes (bool): booleano que indica si existen los recursos sufientes.
                result (dict): resultado de la operacion con el fin de loggear las operaciones realizadas
            
        '''
        recursos_suficientes = True
        print('[+] Recursos separados correctamente en la base de datos')
        result = {
            'valor': 6,
            'mensaje': 'Recursos separados correctamente en la base de datos'
        }

        return [recursos_suficientes, result]

    def listar_workers_actuales(self, id_topologia) -> None:
        print('Actualmente su topologia cuenta con: '+str(['worker1', 'worker2']))
        print()

    def workers_info_slice(self, id_topologia) -> str:
        '''
            A apartir del ID de una topologia, se define que tipo de infraestructura usa y se 
            devuelve la tabla para esa infraestructura.
        '''
        return self.workers_info()['openstack']

    def eliminar_topologia(self, id_topologia) -> dict:
        print('\n[-] Se eliminó correctamente')
        return {
            'valor': 6,
            'mensaje': 'Topologia eliminada correctamente'
        }

    def crear_vm(self, data) -> dict:
        print('[+] VM creada correctamente')
        result = None  # codigo sislog
        return result

    def agregar_nodo(self, data) -> dict:
        print('[+] Se agregó correctamente')
        result = {
            'valor': 6,
            'mensaje': 'Maquina virtual creada satisfactoriamente'
        }
        return result

    def listar_nodos(self, id_topologia) -> None:
        t = PrettyTable()
        t.field_names = ["ID",  "Nombre"]
        t.add_row(["1", "Nodo 1"])
        t.add_row(["2", "Nodo 2"])
        t.add_row(["3", "Nodo 3"])
        t.add_row(["4", "Nodo 4"])
        t = '\n' + str(t)
        t = t.replace("\n", "\n                ")
        print(t)

    def eliminar_nodo(self, id_topologia, id_nodo) -> dict:
        print('\n[-] Se eliminó correctamente')
        result = {
            'valor': 6,
            'mensaje': 'Maquina virtual eliminada satisfactoriamente'
        }
        return result

    def aumentar_slice(self, data) -> dict:
        print('\n[+] Slice aumentado exitosamente')
        result = {
            'valor': 6,
            'mensaje': 'Slice aumentado exitosamente'
        }
        return result

    def conectar_nodo_internet(self, id_nodo) -> dict:
        print('\n[+] Conexión exitosa')
        return {
            'valor': 6,
            'mensaje': 'Conexion de nodo a internet satisfactoria'
        }

    def conectar_topologias(self, id_topologia1, id_topologia2) -> dict:
        print('\n[+] Conexión exitosa')
        return {
            'valor': 6,
            'mensaje': 'Conexion entre slices satisfactorio'
        }
