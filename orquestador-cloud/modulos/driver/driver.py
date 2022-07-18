#!/usr/bin/env python3

from datetime import datetime
from prettytable import PrettyTable
import pandas as pd
import json
import random

from .ssh import SSH
from .db import DB
from .openstackapi import OpenstackApi
from ..logging.Logging import Logging

from ..config.crendentials import config_controller_lc
from ..config.crendentials import config_db_linuxcluster
from ..config.crendentials import config_w1_lc
from ..config.crendentials import config_w2_lc
from ..config.crendentials import config_w3_lc

from ..config.crendentials import config_openstack
from ..config.crendentials import config_db_openstack
from ..config.crendentials import config_controller_openstack
from ..config.crendentials import config_w1_openstack
from ..config.crendentials import config_w2_openstack
from ..config.crendentials import config_w3_openstack


class Driver():
    def __init__(self) -> None:
        self.logging = Logging()
        
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
        self.openstackapi = OpenstackApi(   config_openstack['OS_USERNAME'], 
                                            config_openstack['OS_PASSWORD'], 
                                            config_openstack['OS_USER_DOMAIN_NAME'], 
                                            config_openstack['OS_PROJECT_DOMAIN_NAME'], 
                                            config_openstack['OS_PROJECT_NAME'], 
                                            config_openstack['OS_AUTH_URL'], 
                                            config_openstack['COMPUTE_URL'], 
                                            config_openstack['NETWORK_URL'], 
                                            config_openstack['GLANCE_URL'])
        self.openstack_control = SSH(config_controller_openstack['host'],
                                     config_controller_openstack['port'],
                                     config_controller_openstack['username'],
                                     config_controller_openstack['private_key'],
                                     config_controller_openstack['passphrase'])
        self.openstack_worker1 = SSH(config_w1_openstack['host'],
                                     config_w1_openstack['port'],
                                     config_w1_openstack['username'],
                                     config_w1_openstack['private_key'],
                                     config_w1_openstack['passphrase'])
        self.openstack_worker2 = SSH(config_w2_openstack['host'],
                                     config_w2_openstack['port'],
                                     config_w2_openstack['username'],
                                     config_w2_openstack['private_key'],
                                     config_w2_openstack['passphrase'])
        self.openstack_worker3 = SSH(config_w3_openstack['host'],
                                     config_w3_openstack['port'],
                                     config_w3_openstack['username'],
                                     config_w3_openstack['private_key'],
                                     config_w3_openstack['passphrase'])
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

    # Funciones completadas

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
            db = self.linuxc_db
        elif (nueva_topologia['infraestructura']['infraestructura'] == "OpenStack"):
            db = self.openstack_db

        recursos_suficientes = None
        # se obtiene los ID de los workers dentro de la AZ
        az = nueva_topologia['infraestructura']['az']
        workers_db = db.obtener_workers()
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

    def recursos_suficientes_nodo(self, nuevo_nodo) -> bool:
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
        '''
            Dada la informacion ingresada por el usuario, se verifica que existan los recursos suficientes 
            haciendo la consulta a la DB de la infraestructura correspondiente.

            De ser asi, se se retorna un 'True'. 
            Sino, se retorna un 'False' indicando que no existen los recursos suficientes.

            inputs
            ---
                nuevo_nodo (dict): diccionario que almacena la informacion de la topologia a separar.

                    {
                        'id_topologia': "1",
                        "nombre": 'vm1',
                        "n_vcpus": 1,
                        "memoria": 1,
                        "filesystem": {
                            "filesystem": "CopyOnWrite",
                            "size": 1
                        },
                        "imagen_id": 19,
                        "internet": True
                    }
            
            outputs
            ---
                recursos_suficientes (bool): booleano que indica si existen los recursos sufientes.
            
        '''
        recursos_suficientes = None

        # se define que conexion a db se va a usar
        if (int(nuevo_nodo['id_topologia']) < 1000):
            db = self.linuxc_db
        elif (int(nuevo_nodo['id_topologia']) < 2000):
            db = self.openstack_db

        # con el ID se obtiene el az
        az = db.get("select Worker_idWorker from Topologia_has_Worker where Topologia_idTopologia=%s", nuevo_nodo['id_topologia'])
        az = [ str(a['Worker_idWorker']) for a in az]

        workers_db = db.obtener_workers()
        # se obtiene una lista con la informacion de los workers dentro del AZ (workers_validos)
        workers_validos = [] 
        for worker in workers_db:
            if (str(worker['idWorker']) in az):
                workers_validos.append(worker)
        # se itera sobre cada vm para verificar si hay recursos suficientes
        for worker in workers_validos:
            if ( (int(worker['vcpuLibres'])>=nuevo_nodo['n_vcpus']) and (int(worker['memoriaLibre'])>=nuevo_nodo['memoria']) and (int(worker['discoLibre'])>=nuevo_nodo['filesystem']['size'])):
                recursos_suficientes = True
                break
            else:
                recursos_suficientes = False

        return recursos_suficientes

    def listar_topologias(self) -> None:
        ''' 
            Hace dos cosas:
            1. Imprime la tabla que arma con un objeto PrettyTable()
            2. Arma una lista de diccionarios con la data
        '''
        list_topology = []

        # obtener data de la db
        linuxc_db = self.linuxc_db.obtener_topologias()
        openstack_db = self.openstack_db.obtener_topologias()
        # armar tabla
        x = PrettyTable()
        x.field_names = ["ID", "Nombre", "Tipo", "Infraestructura"]
        for row in linuxc_db:
            x.add_row([row['idTopologia'], row['nombre'], row['tipo'], 'Linux Cluster'])
            list_topology.append({
                'idTopologia':row['idTopologia'], 
                'nombre': row['nombre'], 
                'tipo': row['tipo'], 
                'infraestructura': 'Linux Cluster'
            })
        for row in openstack_db:
            x.add_row([row['idTopologia'], row['nombre'], row['tipo'], 'OpenStack'])
            list_topology.append({
                'idTopologia':row['idTopologia'], 
                'nombre': row['nombre'], 
                'tipo': row['tipo'], 
                'infraestructura': 'OpenStack'
            })
        # Espaciado antes de imprimar la tabla
        x = '\n' + str(x)
        x = x.replace("\n", "\n                ")
        print(x)

        return list_topology
    
    def importar_imagen(self, data) -> dict:
        try: 
            if (data['opcion'] == 1):
                # Subir archivo local
                # 1. Linux Cluster
                self.linuxc_worker1.subir_archivo(data['ruta'], '/home/w1/imagenes/'+data['categoria']+'/'+data['nombre'])
                self.linuxc_worker2.subir_archivo(data['ruta'], '/home/w2/imagenes/'+data['categoria']+'/'+data['nombre'])
                self.linuxc_worker3.subir_archivo(data['ruta'], '/home/wk3/imagenes/'+data['categoria']+'/'+data['nombre'])
                # 2. OpenStack
                self.openstack_control.subir_archivo(data['ruta'], '/home/proyecto/imagenes/'+data['nombre'])
                self.openstack_control.ejecutar_script_local('./modulos/driver/bash_scripts/glance_create_image.sh', [data['nombre'], '/home/proyecto/imagenes/'+data['nombre'], 'qcow2'])
            elif(data['opcion'] == 2):
                # Subir desde URL
                # 1. Linux Cluster
                self.linuxc_worker1.ejecutar_comando('wget '+data['url']+' -O /home/w1/imagenes/'+data['categoria']+'/'+data['nombre'])
                self.linuxc_worker2.ejecutar_comando('wget '+data['url']+' -O /home/w2/imagenes/'+data['categoria']+'/'+data['nombre'])
                self.linuxc_worker3.ejecutar_comando('wget '+data['url']+' -O /home/wk3/imagenes/'+data['categoria']+'/'+data['nombre'])
                # 2. Openstack
                self.openstack_control.ejecutar_comando('wget '+data['url']+' -O /home/proyecto/imagenes/'+data['nombre'])
                self.openstack_control.ejecutar_script_local('./modulos/driver/bash_scripts/glance_create_image.sh', [data['nombre'], '/home/proyecto/imagenes/'+data['nombre'], 'qcow2'])

            last_imageid = self.linuxc_db.get('select max(idImagen) from Imagen')[0]['max(idImagen)']
            image_id = str(last_imageid+1)

            self.linuxc_db.save("INSERT INTO Imagen (idImagen, nombre, categoria, fechaUltimoUso) VALUES (%s, %s,%s,%s)", (image_id, data['nombre'], data['categoria'], str(datetime.today().strftime('%Y-%m-%d'))))
            self.logging.log({ 'valor': 6, 'agent': 'linuxcluster', "mensaje": 'Imagen importada correctamente en /home/w1/imagenes/'+data['categoria']+'/'+data['nombre'] })
            self.logging.log({ 'valor': 6, 'agent': 'linuxcluster', "mensaje": 'Imagen importada correctamente en /home/w2/imagenes/'+data['categoria']+'/'+data['nombre'] })
            self.logging.log({ 'valor': 6, 'agent': 'linuxcluster', "mensaje": 'Imagen importada correctamente en /home/wk3/imagenes/'+data['categoria']+'/'+data['nombre'] })

            self.openstack_db.save("INSERT INTO Imagen (idImagen, nombre, categoria, fechaUltimoUso) VALUES (%s, %s,%s,%s)", (image_id, data['nombre'], data['categoria'], str(datetime.today().strftime('%Y-%m-%d'))))
            self.logging.log({ 'valor': 6, 'agent': 'openstack', "mensaje": "Imagen importada correctamente en /home/proyecto/imagenes/"+data['nombre'] })

            print('\n[+] Imagen importada correctamente')
            return {
                    'valor': 6,
                    'mensaje': 'Imagen importada correctamente en todas las infraestructuras | INSERT INTO Imagen (idImagen, nombre, categoria, fechaUltimoUso) VALUES (%s, %s,%s,%s)' % (image_id, data['nombre'], data['categoria'], str(datetime.today().strftime('%Y-%m-%d')))
                }
        except Exception as e:
            print('[x] '+str(e))
            return {
                'valor': 3,
                'mensaje': 'ERROR al importar imagen | '+str(e)
            }

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

        workers_db = self.openstack_db.get('select * from Worker')
        for worker in workers_db:
            # se obtiene el CPU avg
            if worker['hostname'] == 'worker1':
                list_cpu_usage = self.openstack_worker1.list_cpu_usage('/home/worker/worker1_cpu_metrics')
                cpu_avg = self.cpu_exponential_weigted_average(list_cpu_usage)  # exponential weigted average
            elif worker['hostname'] == 'worker2':
                # Worker 2
                list_cpu_usage = self.openstack_worker2.list_cpu_usage('/home/worker/worker2_cpu_metrics')
                cpu_avg = self.cpu_exponential_weigted_average(list_cpu_usage)  # exponential weigted average
            elif worker['hostname'] == 'worker3':
                # Worker 3
                list_cpu_usage = self.openstack_worker3.list_cpu_usage('/home/worker/worker3_cpu_metrics')
                cpu_avg = self.cpu_exponential_weigted_average(list_cpu_usage)  # exponential weigted average
            # se llena los datos 
            cpu_avg = round(cpu_avg*100, 2) # se limita a 2 decimales
            cpu_avg = str(cpu_avg)+'%'
            tabla_openstack.add_row([worker['idWorker'], worker['hostname'], cpu_avg, worker['vcpuLibres'],worker['memoriaLibre'],worker['discoLibre'],])
        
        tabla_openstack = str(tabla_openstack)
        tabla_openstack = '                '+tabla_openstack
        tabla_openstack = tabla_openstack.replace("\n", "\n                ")
        # 2. tabla_lc
        tabla_lc = PrettyTable()
        tabla_lc.field_names = ["ID", "Nombre", "Porcentaje de uso de CPU", "cantidad disponible de vCPU",
                                "cantidad de memoria libre", "cantidad de disco libre"]

        workers_db = self.linuxc_db.get('select * from Worker')
        for worker in workers_db:
            # se obtiene el CPU avg
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
            # se llena los datos 
            cpu_avg = round(cpu_avg*100, 2) # se limita a 2 decimales
            cpu_avg = str(cpu_avg)+'%'
            tabla_lc.add_row([worker['idWorker'], worker['hostname'], cpu_avg, worker['vcpuLibres'],worker['memoriaLibre'],worker['discoLibre'],])

        tabla_lc = str(tabla_lc)
        tabla_lc = '                '+tabla_lc
        tabla_lc = tabla_lc.replace("\n", "\n                ")

        return {
            'openstack': tabla_openstack,
            'linux_cluster': tabla_lc
        }

    def listar_nodos(self, id_topologia) -> None:

        if id_topologia<1000:
            db = self.linuxc_db
        elif id_topologia<2000:
            db = self.openstack_db

        t = PrettyTable()
        t.field_names = ["ID",  "Nombre", "vCPU", "Memoria (GB)", 'Filesystem', 'Disco (GB)']

        nodos = db.get(' select * from VM where Topologia_idTopologia=%s', id_topologia)
        for nodo in nodos:
            t.add_row([nodo['idVM'], nodo['nombre'], nodo['vCPU'], nodo['memoria'], nodo['tipoFilesystem'], nodo['tamaño']])

        t = '\n' + str(t)
        t = t.replace("\n", "\n                ")
        print(t)

    def listar_workers_actuales(self, id_topologia) -> None:
        '''
            Funcion usada para aumentar la capacidad de un slice.

            Imprime infomacion que contiene una lista de los IDs de los workers que comprende una topologia.
        '''
        if id_topologia < 1000:
            db = self.linuxc_db
        elif id_topologia < 2000:
            db = self.openstack_db
        
        id_workers = db.get('select Worker_idWorker from Topologia_has_Worker where Topologia_idTopologia = %s', id_topologia)
        id_workers = [worker['Worker_idWorker'] for worker in id_workers]

        print('Actualmente su topologia cuenta con: '+str(id_workers))
        print()

    def workers_info_slice(self, id_topologia) -> str:
        '''
            A apartir del ID de una topologia, se define que tipo de infraestructura usa y se 
            devuelve la tabla para esa infraestructura.
        '''
        if id_topologia < 1000:
            return self.workers_info()['linux_cluster']
        elif id_topologia < 2000:
            return self.workers_info()['openstack']

    def aumentar_slice(self, id_workers_agregar, id_topologia) -> dict:
        '''
            id_workers_agregar(list):

                ['1', '2', '3']

            id_topologia(int)
        '''

        worker_agregados = []

        if id_topologia < 1000:
            # Linux Cluster

            workers_actuales = self.linuxc_db.get('select Worker_idWorker from Topologia_has_Worker where Topologia_idTopologia = %s;', id_topologia)
            workers_actuales = [str(worker['Worker_idWorker']) for worker in workers_actuales] # ['1', '2']

            for id_worker in id_workers_agregar:
                if id_worker not in workers_actuales:
                    # si no esta se agrega (si ya esta se ignora)
                    self.linuxc_db.save("insert into Topologia_has_Worker (Topologia_idTopologia, Worker_idWorker) values (%s, %s)", (id_topologia, id_worker))
                    worker_agregados.append(id_worker)
 

        elif id_topologia < 2000:
            # TODO Openstack
            pass

        print('\n[+] Slice aumentado exitosamente')
        result = {
                'valor': 6,
                'mensaje': 'Slice aumentado exitosamente | Topologia ID : '+str(id_topologia)+' | Workers agregados : '+str(worker_agregados),
                'agent': 'linuxcluster'
            }
        return  result

    # Funciones en desarrollo

    def agregar_nodo(self, nodo, debug=False) -> dict:
        '''

            nodo(dict):

                {
                    'id_topologia': "54",
                    "nombre": 'vm1',
                    "n_vcpus": 1,
                    "memoria": 1,
                    "filesystem": {
                        "filesystem": "CopyOnWrite",
                        "size": 1
                    },
                    "imagen_id": 19,
                    "internet": True
                }
        '''

        topology_id = int(nodo['id_topologia'])
        if topology_id < 1000:
            # Linux Cluster
            tipo_topologia = self.linuxc_db.get('select * from Topologia where idTopologia=%s;', topology_id)[0]['tipo']
            if debug: print('Tipo de topologia: '+tipo_topologia)

            if tipo_topologia == 'lineal':
            
                # se obtiene los ID de los workers dentro de la AZ
                az = self.linuxc_db.get("select Worker_idWorker from Topologia_has_Worker where Topologia_idTopologia=%s", topology_id)
                az = [ str(a['Worker_idWorker']) for a in az] # ['1', '2']

                # 1. filter
                workers = self.filter(nodo, az)
                  
                # 2. obtener worker asignado
                worker_asignado = self.scheduler(workers)
                    
                # 3. desplegar vm

                # 3.1 se obtiene informacion base
                vlan_id = self.linuxc_db.get('select * from Vlan where Topologia_idTopologia=%s', topology_id)[0]['idVlan']
                imagen = self.linuxc_db.get("select * from Imagen where idImagen=%s", nodo['imagen_id'])[0]
                id_interfaz = (int(self.linuxc_db.get('select max(idInterfaz) from Interfaz')[0]['max(idInterfaz)']) + 1 ) if self.linuxc_db.get('select max(idInterfaz) from Interfaz')[0]['max(idInterfaz)'] else 1 # para el puerto VNC se toma el id de la ultima interfaz creada (como es topologia lineal solo hay una interfaz por VM) y se le suma 5900 (que es el puerto a partir del cual se deifine las conexiones vnc) y se le suma 1 para obtener el puerto VNC de la nueva VM
                vnc_port = id_interfaz + 5900
                id_vm = (int(self.linuxc_db.get('select max(idVM) from VM')[0]['max(idVM)']) + 1) if self.linuxc_db.get('select max(idVM) from VM')[0]['max(idVM)'] else 1
                mac = "02:00:00:%02x:%02x:%02x" % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

                # 3.2 se ejecuta script de acuerdo a donde se va desplegar
                if worker_asignado['hostname'] == 'worker1':

                    ruta_imagen = '/home/w1/imagenes/'+imagen['categoria']+'/'+imagen['nombre']
                    ruta_fs = '/home/w1/filesystems/n'+str(id_vm)+'.qcow2'
                    if debug: print('worker1 create_vm.sh (%s, %s, %s, %s, %s, %s)' % ("n"+str(id_vm), str(vlan_id), str(vnc_port), ruta_imagen, mac, ruta_fs, str(nodo['n_vcpus']), str(nodo['memoria'])+"G", str(nodo['filesystem']['size'])+"G"))
                    self.linuxc_worker1.ejecutar_script_local('./modulos/driver/bash_scripts/create_vm.sh', ["n"+str(id_vm), str(vlan_id), str(vnc_port), ruta_imagen, mac, ruta_fs, str(nodo['n_vcpus']), str(nodo['memoria'])+"G", str(nodo['filesystem']['size'])+"G"])

                    print('''[+] Maquina virtual desplegara en Worker 1, 
    Acceda a su maquina estableciendo un tunel SSH para luego conectarse por VNC en localhost
    Ejemplo: ssh -L  %s:127.0.0.1:%s acceso_vnc@10.20.12.161 -p 2201''' % (vnc_port, vnc_port))

                elif worker_asignado['hostname'] == 'worker2':

                    ruta_imagen = '/home/w2/imagenes/'+imagen['categoria']+'/'+imagen['nombre']
                    ruta_fs = '/home/w2/filesystems/n'+str(id_vm)+'.qcow2'
                    vm_identifier = "n"+str(id_vm)
                    if debug: print('worker2 create_vm.sh (%s, %s, %s, %s, %s, %s)' % (vm_identifier, str(vlan_id), str(vnc_port), ruta_imagen, mac, ruta_fs, str(nodo['n_vcpus']), str(nodo['memoria'])+"G", str(nodo['filesystem']['size'])+"G"))
                    self.linuxc_worker2.ejecutar_script_local('./modulos/driver/bash_scripts/create_vm.sh', ["n"+str(id_vm), str(vlan_id), str(vnc_port), ruta_imagen, mac, ruta_fs, str(nodo['n_vcpus']), str(nodo['memoria'])+"G", str(nodo['filesystem']['size'])+"G"])

                    print('''[+] Maquina virtual desplegara en Worker 2, 
    Acceda a su maquina estableciendo un tunel SSH para luego conectarse por VNC en localhost
    Ejemplo: ssh -L  %s:127.0.0.1:%s acceso_vnc@10.20.12.161 -p 2202''' % (vnc_port, vnc_port))

                elif worker_asignado['hostname'] == 'worker3':

                    ruta_imagen = '/home/wk3/imagenes/'+imagen['categoria']+'/'+imagen['nombre']
                    ruta_fs = '/home/wk3/filesystems/n'+str(id_vm)+'.qcow2'
                    if debug: print('worker3 create_vm.sh (%s, %s, %s, %s, %s, %s)' % ("n"+str(id_vm), str(vlan_id), str(vnc_port), ruta_imagen, mac, ruta_fs, str(nodo['n_vcpus']), str(nodo['memoria'])+"G", str(nodo['filesystem']['size'])+"G"))
                    self.linuxc_worker3.ejecutar_script_local('./modulos/driver/bash_scripts/create_vm.sh', ["n"+str(id_vm), str(vlan_id), str(vnc_port), ruta_imagen, mac, ruta_fs, str(nodo['n_vcpus']), str(nodo['memoria'])+"G", str(nodo['filesystem']['size'])+"G"])

                    print('''[+] Maquina virtual desplegara en Worker 3, 
    Acceda a su maquina estableciendo un tunel SSH para luego conectarse por VNC en localhost
    Ejemplo: ssh -L  %s:127.0.0.1:%s acceso_vnc@10.20.12.161 -p 2203''' % (vnc_port, vnc_port))

                # 4. guardar info en DB
                internet = 1 if nodo['internet']==True else 0
                self.linuxc_db.save("insert into VM (idVM, nombre, Topologia_idTopologia, Imagen_idImagen, Worker_idWorker, vCPU, memoria, tipoFilesystem, tamaño) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (str(id_vm), nodo['nombre'], str(topology_id), str(nodo['imagen_id']), str(worker_asignado['idWorker']), str(nodo['n_vcpus']), str(nodo['memoria']), nodo['filesystem']['filesystem'], str(nodo['filesystem']['size'])))
                if debug: print("insert into VM (idVM, nombre, Topologia_idTopologia, Imagen_idImagen, Worker_idWorker, vCPU, memoria, tipoFilesystem, tamaño) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)" % (str(id_vm), nodo['nombre'], str(topology_id), str(nodo['imagen_id']), str(worker_asignado['idWorker']), str(nodo['n_vcpus']), str(nodo['memoria']), nodo['filesystem']['filesystem'], str(nodo['filesystem']['size'])))
                self.linuxc_db.save("insert into Interfaz (idInterfaz, nombre, mac, VM_idVM, Vlan_idVlan, internet, target) VALUES (%s, %s, %s, %s, %s, %s, %s)", (str(id_interfaz), 'link_1', mac, str(id_vm), str(vlan_id), str(internet), str(-1) ))
                if debug: print(("insert into Interfaz (idInterfaz, nombre, mac, VM_idVM, Vlan_idVlan, internet, target) VALUES (%s, %s, %s, %s, %s, %s, %s)" % (str(id_interfaz), 'link_1', mac, str(id_vm), str(vlan_id), str(internet), str(-1) )))

                # 5. se restan recursos en workers
                cpu_restante = int(worker_asignado['vcpuLibres']) - int(nodo['n_vcpus'])
                memoria_restante = int(worker_asignado['memoriaLibre']) - int(nodo['memoria'])
                disco_restante = int(worker_asignado['discoLibre']) - int(nodo['filesystem']['size'])
                self.linuxc_db.save("UPDATE Worker SET vcpuLibres=%s, memoriaLibre=%s, discoLibre=%s where idWorker=%s", (cpu_restante, memoria_restante, disco_restante, worker_asignado['idWorker']))
                if debug: print("UPDATE Worker SET vcpuLibres=%s, memoriaLibre=%s, discoLibre=%s where idWorker=%s" % (cpu_restante, memoria_restante, disco_restante, worker_asignado['idWorker']))

        elif topology_id < 2000:
            # Openstack
            pass

        print('[+] Se agregó correctamente')
        result = {
            'valor': 6,
            'mensaje': 'Maquina virtual creada satisfactoriamente | '+str(nodo)
        }
        return result

    def crear_topologia(self, nueva_topologia, debug=False) -> dict:
        if (nueva_topologia['infraestructura']['infraestructura'] == "Linux Cluster"):
            last_topologyid = self.linuxc_db.get('select max(idTopologia) from Topologia')[0]['max(idTopologia)'] if self.linuxc_db.get('select max(idTopologia) from Topologia')[0]['max(idTopologia)'] else 0
            topology_id = str(last_topologyid+1)
            last_vlanid = self.linuxc_db.get('select max(idVlan) from Vlan')[0]['max(idVlan)'] if self.linuxc_db.get('select max(idVlan) from Vlan')[0]['max(idVlan)'] else 0
            
            if nueva_topologia['tipo'] == 'lineal':
                # Tipo: Lineal
                # 1. Crear la(s) red(es) 
                vlan_id = str(last_vlanid + 1)
                nombre = nueva_topologia['nombre']
                red = "192.168."+vlan_id+".0/24"
                gateway = "192.168."+vlan_id+".1"
                gateway_w_netmask = "192.168."+vlan_id+".1/24"
                dhcp_ip = "192.168."+vlan_id+".2/24"
                dhcp_range = "192.168."+vlan_id+".10,192.168."+vlan_id+".254,255.255.255.0"

                # try:
                if debug: print('create_network.sh [%s, %s, %s, %s, %s, %s, %s]' % (nombre+str(vlan_id), vlan_id, red, gateway, dhcp_ip, dhcp_range, gateway_w_netmask))
                self.linuxc_controller.ejecutar_script_local('./modulos/driver/bash_scripts/create_network.sh', [nombre+str(vlan_id), vlan_id, red, gateway, dhcp_ip, dhcp_range, gateway_w_netmask])

                if debug: print("INSERT INTO Topologia (idTopologia, nombre, tipo) VALUES (%s,%s,%s)" % (str(topology_id), nueva_topologia['nombre'], 'lineal'))
                self.linuxc_db.save("INSERT INTO Topologia (idTopologia, nombre, tipo) VALUES (%s,%s,%s)", (str(topology_id), nueva_topologia['nombre'], 'lineal'))

                if debug: print("INSERT INTO Vlan (idVlan, gateway, dhcpServer, network, Topologia_idTopologia) VALUES (%s, %s, %s, %s, %s)" % (int(vlan_id), gateway_w_netmask, dhcp_ip, red, int(topology_id) ))
                self.linuxc_db.save("INSERT INTO Vlan (idVlan, gateway, dhcpServer, network, Topologia_idTopologia) VALUES (%s, %s, %s, %s, %s)", (int(vlan_id), gateway_w_netmask, dhcp_ip, red, int(topology_id) ))

                for worker_id in nueva_topologia['infraestructura']['az']:
                        self.linuxc_db.save("INSERT INTO Topologia_has_Worker (Topologia_idTopologia, Worker_idWorker) VALUES (%s,%s)", (topology_id, worker_id))
                        if debug: print("INSERT INTO Topologia_has_Worker (Topologia_idTopologia, Worker_idWorker) VALUES (%s,%s)" % (topology_id, worker_id))

                # 2. Despliegue de VMs
                # se obtiene los ID de los workers dentro de la AZ
                az = nueva_topologia['infraestructura']['az']
                # se analiza para cada VM
                for vm in nueva_topologia['vms']:

                    # 1. filter
                    workers = self.filter(vm, az)
                  
                    # 2. obtener worker asignado
                    worker_asignado = self.scheduler(workers)
                    # 3. desplegar vm

                    # 3.1 se obtiene informacion base
                    imagen = self.linuxc_db.get("select * from Imagen where idImagen=%s", vm['imagen_id'])[0]
                    id_interfaz = (int(self.linuxc_db.get('select max(idInterfaz) from Interfaz')[0]['max(idInterfaz)']) + 1 ) if self.linuxc_db.get('select max(idInterfaz) from Interfaz')[0]['max(idInterfaz)'] else 1 # para el puerto VNC se toma el id de la ultima interfaz creada (como es topologia lineal solo hay una interfaz por VM) y se le suma 5900 (que es el puerto a partir del cual se deifine las conexiones vnc) y se le suma 1 para obtener el puerto VNC de la nueva VM
                    vnc_port = id_interfaz + 5900
                    id_vm = (int(self.linuxc_db.get('select max(idVM) from VM')[0]['max(idVM)']) + 1) if self.linuxc_db.get('select max(idVM) from VM')[0]['max(idVM)'] else 1
                    mac = "02:00:00:%02x:%02x:%02x" % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

                    # 3.2 se ejecuta script de acuerdo a donde se va desplegar
                    if worker_asignado['hostname'] == 'worker1':
                        
                        ruta_imagen = '/home/w1/imagenes/'+imagen['categoria']+'/'+imagen['nombre']
                        ruta_fs = '/home/w1/filesystems/n'+str(id_vm)+'.qcow2'
                        if debug: print('worker1 create_vm.sh (%s, %s, %s, %s, %s, %s)' % ("n"+str(id_vm), str(vlan_id), str(vnc_port), ruta_imagen, mac, ruta_fs, str(vm['n_vcpus']), str(vm['memoria'])+"G", str(vm['filesystem']['size'])+"G"))
                        self.linuxc_worker1.ejecutar_script_local('./modulos/driver/bash_scripts/create_vm.sh', ["n"+str(id_vm), str(vlan_id), str(vnc_port), ruta_imagen, mac, ruta_fs, str(vm['n_vcpus']), str(vm['memoria'])+"G", str(vm['filesystem']['size'])+"G"])
                        print('''[+] Maquina virtual desplegara en Worker 1, 
    Acceda a su maquina estableciendo un tunel SSH para luego conectarse por VNC en localhost
    Ejemplo: ssh -L  %s:127.0.0.1:%s acceso_vnc@10.20.12.161 -p 2201''' % (vnc_port, vnc_port))

                        #print('[+] Acceso por consola en puerto %s del controller %s' % (vnc_port, config_db_linuxcluster['host']))

                    elif worker_asignado['hostname'] == 'worker2':

                        ruta_imagen = '/home/w2/imagenes/'+imagen['categoria']+'/'+imagen['nombre']
                        ruta_fs = '/home/w2/filesystems/n'+str(id_vm)+'.qcow2'
                        vm_identifier = "n"+str(id_vm)
                        if debug: print('worker2 create_vm.sh (%s, %s, %s, %s, %s, %s)' % (vm_identifier, str(vlan_id), str(vnc_port), ruta_imagen, mac, ruta_fs, str(vm['n_vcpus']), str(vm['memoria'])+"G", str(vm['filesystem']['size'])+"G"))
                        self.linuxc_worker2.ejecutar_script_local('./modulos/driver/bash_scripts/create_vm.sh', ["n"+str(id_vm), str(vlan_id), str(vnc_port), ruta_imagen, mac, ruta_fs, str(vm['n_vcpus']), str(vm['memoria'])+"G", str(vm['filesystem']['size'])+"G"])
                        print('''[+] Maquina virtual desplegara en Worker 2, 
    Acceda a su maquina estableciendo un tunel SSH al Worker para luego conectarse por VNC en localhost      
    Ejemplo: ssh -L  %s:127.0.0.1:%s acceso_vnc@10.20.12.161 -p 2202''' % (vnc_port, vnc_port))

                    elif worker_asignado['hostname'] == 'worker3':

                        ruta_imagen = '/home/wk3/imagenes/'+imagen['categoria']+'/'+imagen['nombre']
                        ruta_fs = '/home/wk3/filesystems/n'+str(id_vm)+'.qcow2'
                        if debug: print('worker3 create_vm.sh (%s, %s, %s, %s, %s, %s)' % ("n"+str(id_vm), str(vlan_id), str(vnc_port), ruta_imagen, mac, ruta_fs, str(vm['n_vcpus']), str(vm['memoria'])+"G", str(vm['filesystem']['size'])+"G"))
                        self.linuxc_worker3.ejecutar_script_local('./modulos/driver/bash_scripts/create_vm.sh', ["n"+str(id_vm), str(vlan_id), str(vnc_port), ruta_imagen, mac, ruta_fs, str(vm['n_vcpus']), str(vm['memoria'])+"G", str(vm['filesystem']['size'])+"G"])
                        print('''[+] Maquina virtual desplegara en Worker 3, 
    Acceda a su maquina estableciendo un tunel SSH para luego conectarse por VNC en localhost                     
    Ejemplo: ssh -L  %s:127.0.0.1:%s acceso_vnc@10.20.12.161 -p 2202''' % (vnc_port, vnc_port))

                        
                    # 4. guardar info en DB
                    internet = 1 if vm['internet']==True else 0
                    self.linuxc_db.save("insert into VM (idVM, nombre, Topologia_idTopologia, Imagen_idImagen, Worker_idWorker, vCPU, memoria, tipoFilesystem, tamaño) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (str(id_vm), vm['nombre'], str(topology_id), str(vm['imagen_id']), str(worker_asignado['idWorker']), str(vm['n_vcpus']), str(vm['memoria']), vm['filesystem']['filesystem'], str(vm['filesystem']['size'])))
                    if debug: print("insert into VM (idVM, nombre, Topologia_idTopologia, Imagen_idImagen, Worker_idWorker, vCPU, memoria, tipoFilesystem, tamaño) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)" % (str(id_vm), vm['nombre'], str(topology_id), str(vm['imagen_id']), str(worker_asignado['idWorker']), str(vm['n_vcpus']), str(vm['memoria']), vm['filesystem']['filesystem'], str(vm['filesystem']['size'])))
                    self.linuxc_db.save("insert into Interfaz (idInterfaz, nombre, mac, VM_idVM, Vlan_idVlan, internet, target) VALUES (%s, %s, %s, %s, %s, %s, %s)", (str(id_interfaz), 'link_1', mac, str(id_vm), str(vlan_id), str(internet), str(-1) ))
                    if debug: print(("insert into Interfaz (idInterfaz, nombre, mac, VM_idVM, Vlan_idVlan, internet, target) VALUES (%s, %s, %s, %s, %s, %s, %s)" % (str(id_interfaz), 'link_1', mac, str(id_vm), str(vlan_id), str(internet), str(-1) )))

                    # 5. se restan recursos en workers
                    cpu_restante = int(worker_asignado['vcpuLibres']) - int(vm['n_vcpus'])
                    memoria_restante = int(worker_asignado['memoriaLibre']) - int(vm['memoria'])
                    disco_restante = int(worker_asignado['discoLibre']) - int(vm['filesystem']['size'])
                    self.linuxc_db.save("UPDATE Worker SET vcpuLibres=%s, memoriaLibre=%s, discoLibre=%s where idWorker=%s", (cpu_restante, memoria_restante, disco_restante, worker_asignado['idWorker']))
                    if debug: print("UPDATE Worker SET vcpuLibres=%s, memoriaLibre=%s, discoLibre=%s where idWorker=%s" % (cpu_restante, memoria_restante, disco_restante, worker_asignado['idWorker']))
                # except Exception as e:
                #     return {
                #         'valor': 3,
                #         'mensaje': 'ERROR en la creacion de la red para topologia lineal | '+str(e).replace('\n', ' \\n ')
                #     }
            else:
                # TODO otro tipo de topologia
                pass

        elif (nueva_topologia['infraestructura']['infraestructura'] == "OpenStack"):
            last_topologyid = self.openstack_db.get('select max(idTopologia) from Topologia')[0]['max(idTopologia)'] if self.openstack_db.get('select max(idTopologia) from Topologia')[0]['max(idTopologia)'] else 0
            topology_id = str(last_topologyid+1)
            last_vlanid = self.openstack_db.get('select max(idVlan) from Vlan')[0]['max(idVlan)'] if self.openstack_db.get('select max(idVlan) from Vlan')[0]['max(idVlan)'] else 0

            
            
            if nueva_topologia['tipo'] == 'lineal':
                # Tipo: Lineal
                # 1. Crear la red
                vlan_id = str(last_vlanid + 1) # TODO actualizar ultimo ID en DB
                nombre = nueva_topologia['nombre']
                red = "192.168."+vlan_id+".0/24"
                gateway_w_netmask = "192.168."+vlan_id+".1/24"
                dhcp_ip = "192.168."+vlan_id+".2/24"

                network_id = self.openstackapi.crear_red(nombre, vlan_id)
                self.openstackapi.crear_subred(network_id, nombre+'_subred', red)
                if debug: print('Red creada en OpenStack: '+ str([network_id, nombre+'_subred', red]))

                if debug: print("INSERT INTO Topologia (idTopologia, nombre, tipo) VALUES (%s,%s,%s)" % (str(topology_id), nueva_topologia['nombre'], 'lineal'))
                self.openstack_db.save("INSERT INTO Topologia (idTopologia, nombre, tipo) VALUES (%s,%s,%s)", (str(topology_id), nueva_topologia['nombre'], 'lineal'))

                if debug: print("INSERT INTO Vlan (idVlan, gateway, dhcpServer, network, Topologia_idTopologia) VALUES (%s, %s, %s, %s, %s)" % (int(vlan_id), gateway_w_netmask, dhcp_ip, red, int(topology_id) ))
                self.openstack_db.save("INSERT INTO Vlan (idVlan, gateway, dhcpServer, network, Topologia_idTopologia) VALUES (%s, %s, %s, %s, %s)", (int(vlan_id), gateway_w_netmask, dhcp_ip, red, int(topology_id) ))

                for worker_id in nueva_topologia['infraestructura']['az']:
                    self.openstack_db.save("INSERT INTO Topologia_has_Worker (Topologia_idTopologia, Worker_idWorker) VALUES (%s,%s)", (topology_id, worker_id))
                    if debug: print("INSERT INTO Topologia_has_Worker (Topologia_idTopologia, Worker_idWorker) VALUES (%s,%s)" % (topology_id, worker_id))

                # 2. Crear VMs
                for vm in nueva_topologia['vms']:
                    nombre = vm['nombre']

                    # definir que flavor en base a los recursos que esta pidiendo (si no existe crear)
                    list_flavors = [
                        {'id': '028e8fd2-b49e-4518-a01f-23505df8c1cb', 'vcpus': 1, 'memoria': 1},
                        {'id': '7b20ec76-66cc-4838-913a-3b5b6cde8a7a', 'vcpus': 1, 'memoria': 2},
                        {'id': '46b8d32a-d861-4e36-8335-91404953821c', 'vcpus': 1, 'memoria': 3},
                    ]
                    if vm['n_vcpus'] == 1 and vm['memoria'] == 1:
                        flavor_id = '028e8fd2-b49e-4518-a01f-23505df8c1cb'
                    elif vm['n_vcpus'] == 1 and vm['memoria'] == 2:
                        flavor_id = '7b20ec76-66cc-4838-913a-3b5b6cde8a7a'
                    elif vm['n_vcpus'] == 1 and vm['memoria'] == 3:
                        flavor_id = '46b8d32a-d861-4e36-8335-91404953821c'
                    if debug: print('favlour_id: '+flavor_id)

                    # importar imagen en openstack
                    nombre_imagen = self.openstack_db.get("select * from Imagen where idImagen=%s", vm['imagen_id'])[0]['nombre']
                    if debug: print('Nombre de imagen de la DB: '+str(nombre_imagen))
                    imagenes = self.openstackapi.listar_imagenes()
                    imagen_id_openstack = None
                    for imagen in imagenes:
                        if imagen['name'] == nombre_imagen:
                            imagen_id_openstack = imagen['id']
                    if debug: print('Imagen OpenStack ID: '+str(imagen_id_openstack))

                    # seleccionar red
                    red_id = network_id

                    # se crea la vm
                    response_vm = self.openstackapi.crear_vm(nombre, flavor_id, imagen_id_openstack, red_id)
                    print('VM Creada:')
                    print(response_vm)
                    print()

                    # actualizar datos en db                
                    id_interfaz = (int(self.openstack_db.get('select max(idInterfaz) from Interfaz')[0]['max(idInterfaz)']) + 1 ) if self.openstack_db.get('select max(idInterfaz) from Interfaz')[0]['max(idInterfaz)'] else 1 # para el puerto VNC se toma el id de la ultima interfaz creada (como es topologia lineal solo hay una interfaz por VM) y se le suma 5900 (que es el puerto a partir del cual se deifine las conexiones vnc) y se le suma 1 para obtener el puerto VNC de la nueva VM
                    id_vm = (int(self.openstack_db.get('select max(idVM) from VM')[0]['max(idVM)']) + 1) if self.openstack_db.get('select max(idVM) from VM')[0]['max(idVM)'] else 1
                    
                    self.openstack_db.save("insert into VM (idVM, nombre, Topologia_idTopologia, Imagen_idImagen, Worker_idWorker, vCPU, memoria, tipoFilesystem, tamaño) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (str(id_vm), vm['nombre'], str(topology_id), str(vm['imagen_id']), str(worker_asignado['idWorker']), str(vm['n_vcpus']), str(vm['memoria']), vm['filesystem']['filesystem'], str(vm['filesystem']['size'])))
                    if debug: print("insert into VM (idVM, nombre, Topologia_idTopologia, Imagen_idImagen, Worker_idWorker, vCPU, memoria, tipoFilesystem, tamaño) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)" % (str(id_vm), vm['nombre'], str(topology_id), str(vm['imagen_id']), str(worker_asignado['idWorker']), str(vm['n_vcpus']), str(vm['memoria']), vm['filesystem']['filesystem'], str(vm['filesystem']['size'])))

                    self.openstack_db.save("insert into Interfaz (idInterfaz, nombre, mac, VM_idVM, Vlan_idVlan, internet, target) VALUES (%s, %s, %s, %s, %s, %s, %s)", (str(id_interfaz), 'link_1', mac, str(id_vm), str(vlan_id), str(internet), str(-1) ))
                    if debug: print(("insert into Interfaz (idInterfaz, nombre, mac, VM_idVM, Vlan_idVlan, internet, target) VALUES (%s, %s, %s, %s, %s, %s, %s)" % (str(id_interfaz), 'link_1', mac, str(id_vm), str(vlan_id), str(internet), str(-1) )))

                    # se restan recursos en workers
                    
                    # cpu_restante = int(worker_asignado['vcpuLibres']) - int(vm['n_vcpus'])
                    # memoria_restante = int(worker_asignado['memoriaLibre']) - int(vm['memoria'])
                    # disco_restante = int(worker_asignado['discoLibre']) - int(vm['filesystem']['size'])
                    #self.openstack_db.save("UPDATE Worker SET vcpuLibres=%s, memoriaLibre=%s, discoLibre=%s where idWorker=%s", (cpu_restante, memoria_restante, disco_restante, worker_asignado['idWorker']))
                    #if debug: print("UPDATE Worker SET vcpuLibres=%s, memoriaLibre=%s, discoLibre=%s where idWorker=%s" % (cpu_restante, memoria_restante, disco_restante, worker_asignado['idWorker']))
                    
                # TODO especifcar az
                # TODO try catch con agent: 'openstackapi'



        print('\n[+] Se creó correctamente')
        return {
            'valor': 6,
            'mensaje': 'Topologia creada correctamente: '+str(nueva_topologia)
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
                        "mac": interfaz['mac'],
                        "conexionInternet": True if (int(interfaz['internet'])==1) else False,
                        "nombre": interfaz['nombre']
                        
                    })
                # parseo final de vm
                vm_parsed.append({
                    "id": vm["idVM"],
                    "nombre": vm["nombre"],
                    "workerID": vm['Worker_idWorker'],
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
                # comando para tunel ssh
                id_interfaz = self.linuxc_db.get('select idInterfaz from Interfaz where VM_idVM=%s LIMIT 1', vm["idVM"])[0]['idInterfaz'] # se toma en cuenta una sola interfaz
                vnc_port = int(id_interfaz) + 5900
                comando_tunel = 'ssh -L  %s:127.0.0.1:%s acceso_vnc@10.20.12.161 -p 220%s' % (vnc_port, vnc_port, vm["Worker_idWorker"])

                # se añade
                vm_parsed.append({
                    "id": vm["idVM"],
                    "name": vm["nombre"],
                    "icon": categoria_imagen,
                    "tunnel_ssh": comando_tunel
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
                        "mac": interfaz['mac'],

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
        return topologia_json_visualizador

    def eliminar_nodo(self, topology_id, id_vm, debug=False) -> dict:

        if topology_id < 1000:
            # Linux Cluster
            tipo_topologia = self.linuxc_db.get('select * from Topologia where idTopologia=%s;', topology_id)[0]['tipo']
            if debug: print('Tipo de topologia: '+tipo_topologia)

            if tipo_topologia == 'lineal':

                vlan_id = self.linuxc_db.get('select * from Vlan where Topologia_idTopologia=%s', topology_id)[0]['idVlan']

                # imagen que esta usando la vm
                id_imagen = self.linuxc_db.get('select Imagen_idImagen from VM where idVM=%s', id_vm)[0]['Imagen_idImagen']
                imagen = self.linuxc_db.get("select * from Imagen where idImagen=%s", id_imagen)[0]
                if debug: print('Imagen: '+str(imagen))

                # interfaz usada por la VM
                id_interfaz = self.linuxc_db.get('select IdInterfaz from Interfaz where VM_idVM=%s', id_vm)[0]['IdInterfaz']
                if debug: print('id_interfaz: '+str(id_interfaz))
                vnc_port = int(id_interfaz) + 5900

                # en que worker esta
                id_worker = int(self.linuxc_db.get('select Worker_idWorker from VM where idVM=%s', id_vm)[0]['Worker_idWorker'])

                if id_worker == 1:

                    ruta_imagen = '/home/w1/imagenes/'+imagen['categoria']+'/'+imagen['nombre']
                    ruta_fs = '/home/w1/filesystems/n'+str(id_vm)+'.qcow2'
                    if debug: print('worker1 delete_vm.sh (%s, %s, %s, %s, %s, %s)' % ("n"+str(id_vm), str(vlan_id), str(vnc_port), ruta_imagen, "-", ruta_fs))
                    self.linuxc_worker1.ejecutar_script_local('./modulos/driver/bash_scripts/delete_vm.sh', ["n"+str(id_vm), str(vlan_id), str(vnc_port), ruta_imagen, "-", ruta_fs])
                    print('[+] vm eliminada en worker 1')

                elif id_worker == 2:

                    ruta_imagen = '/home/w2/imagenes/'+imagen['categoria']+'/'+imagen['nombre']
                    ruta_fs = '/home/w2/filesystems/n'+str(id_vm)+'.qcow2'
                    if debug: print('worker2 delete_vm.sh (%s, %s, %s, %s, %s, %s)' % ("n"+str(id_vm), str(vlan_id), str(vnc_port), ruta_imagen, "-", ruta_fs))
                    self.linuxc_worker2.ejecutar_script_local('./modulos/driver/bash_scripts/delete_vm.sh', ["n"+str(id_vm), str(vlan_id), str(vnc_port), ruta_imagen, "-", ruta_fs])
                    print('[+] vm eliminada en worker 2')

                elif id_worker == 3:
                    
                    ruta_imagen = '/home/wk3/imagenes/'+imagen['categoria']+'/'+imagen['nombre']
                    ruta_fs = '/home/wk3/filesystems/n'+str(id_vm)+'.qcow2'
                    if debug: print('worker3 delete_vm.sh (%s, %s, %s, %s, %s, %s)' % ("n"+str(id_vm), str(vlan_id), str(vnc_port), ruta_imagen, "-", ruta_fs))
                    self.linuxc_worker3.ejecutar_script_local('./modulos/driver/bash_scripts/delete_vm.sh', ["n"+str(id_vm), str(vlan_id), str(vnc_port), ruta_imagen, "-", ruta_fs])
                    print('[+] vm eliminada en worker 3')

                # se restan recursos en workers
                worker_asignado = self.linuxc_db.get('select * from Worker where idWorker=%s', id_worker)[0]
                nodo = self.linuxc_db.get('select * from VM where idVM=%s', id_vm)[0]

                cpu_restante = int(worker_asignado['vcpuLibres']) + int(nodo['vCPU'])
                memoria_restante = int(worker_asignado['memoriaLibre']) + int(nodo['memoria'])
                disco_restante = int(worker_asignado['discoLibre']) + int(nodo['tamaño'])
                self.linuxc_db.save("UPDATE Worker SET vcpuLibres=%s, memoriaLibre=%s, discoLibre=%s where idWorker=%s", (cpu_restante, memoria_restante, disco_restante, worker_asignado['idWorker']))
                if debug: print("UPDATE Worker SET vcpuLibres=%s, memoriaLibre=%s, discoLibre=%s where idWorker=%s" % (cpu_restante, memoria_restante, disco_restante, worker_asignado['idWorker']))

                # guardar info en DB
                self.linuxc_db.save("delete from Interfaz where idInterfaz=%s", (id_interfaz))
                if debug: print("delete from Interfaz where idInterfaz=%s", (id_interfaz))
                self.linuxc_db.save("delete from VM where idVM=%s", (id_vm))
                if debug: print("delete from VM where idVM=%s", (id_vm))

        elif topology_id < 2000:
            # OpenStack
            pass

        print('[-] Se eliminó correctamente')
        result = {
            'valor': 6,
            'mensaje': 'Maquina virtual eliminada satisfactoriamente | '+str(nodo)
        }
        return result

    def eliminar_topologia(self, topology_id, debug=False) -> dict:

        if topology_id < 1000:
            # Linux Cluster

            topologia = self.linuxc_db.get('select * from Topologia where idTopologia=%s;', topology_id)[0]
            tipo_topologia = topologia['tipo']
            if debug: print('Tipo de topologia: '+tipo_topologia)

            if tipo_topologia == 'lineal':

                # 1. Crear la(s) red(es) 
                vlan_id = str(self.linuxc_db.get('select * from Vlan where Topologia_idTopologia=%s', topology_id)[0]['idVlan'])
                nombre = topologia['nombre']
                red = "192.168."+vlan_id+".0/24"
                gateway = "192.168."+vlan_id+".1"
                gateway_w_netmask = "192.168."+vlan_id+".1/24"
                dhcp_ip = "192.168."+vlan_id+".2/24"
                dhcp_range = "192.168."+vlan_id+".10,192.168."+vlan_id+".254,255.255.255.0"

                if debug: print('delete_network.sh [%s, %s, %s, %s, %s, %s, %s]' % (nombre+str(vlan_id), vlan_id, red, gateway, dhcp_ip, dhcp_range, gateway_w_netmask))
                self.linuxc_controller.ejecutar_script_local('./modulos/driver/bash_scripts/delete_network.sh', [nombre+str(vlan_id), vlan_id, red, gateway, dhcp_ip, dhcp_range, gateway_w_netmask])

                vms = self.linuxc_db.get('select * from VM where Topologia_idTopologia=%s', topology_id)
                for vm in vms:
                    self.eliminar_nodo(topology_id, int(vm['idVM']))

                if debug: print("DELETE FROM Topologia_has_Worker where Topologia_idTopologia=%s" % (topology_id))
                self.linuxc_db.save("DELETE FROM Topologia_has_Worker where Topologia_idTopologia=%s", (topology_id))

                if debug: print("DELETE FROM Vlan where Topologia_idTopologia=%s" % (topology_id ))
                self.linuxc_db.save("DELETE FROM Vlan where Topologia_idTopologia=%s", (topology_id))

                if debug: print("DELETE FROM Topologia where idTopologia=%s" % (topology_id))
                self.linuxc_db.save("DELETE FROM Topologia where idTopologia=%s", (topology_id))
                
        elif topology_id < 2000:
            pass

        print('\n[-] Se eliminó topologia correctamente')
        return {
            'valor': 6,
            'mensaje': 'Topologia eliminada correctamente | '+str(topologia)
        }

    
    # Funciones pendientes
    

    def conectar_nodo_internet(self, id_nodo) -> dict:
        print('\n[+] Conexión exitosa')
        return {
            'valor': 6,
            'mensaje': 'Conexion de nodo a internet satisfactoria'
        }