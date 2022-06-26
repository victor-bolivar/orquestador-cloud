from modulos.validador.validador import ValidadorTest
from modulos.logging.Exceptions import InputException

# modulo: validador

def test_obtener_int():
    print('funcion: validador.obtener_int')
    # 1. Se verifca que se valide un entero (sin parametros adicionales)
    correct_result = 100
    input_user = '100'
    result = validador.obtener_int('-', input_user)
    if (result == correct_result):
        print('[+] Se valida un entero correctamente: 100 es entero')
    else: 
        raise Exception('[x] ERROR al validar un entero')
    # 2. Se verifca funcionalidad de maxValor,minValor
    correct_result = 100
    input_user = '100'
    result = validador.obtener_int('-', input_user, minValor=50, maxValor=200)
    if (result == correct_result):
        print('[+] Se valida funcionalidad de maxValor,minValor: se cumple 50<=100<=200')
    else: 
        raise Exception('[x] ERROR al validar funcionalidad de maxValor,minValor (50<=100<=200)')
    # 3. Se verifca funcionalidad de maxValor,minValor
    correct_result = False
    input_user = '500'
    result = validador.obtener_int('-', input_user, minValor=50, maxValor=200)
    if (result == correct_result):
        print('[+] Se valida funcionalidad de maxValor,minValor: se obtiene False al evaluar 500<=200')
    else: 
        raise Exception('[x] ERROR al validar funcionalidad de maxValor,minValor: no se obtiene False al evaluar 500<=200')
    # 4. Se verifca funcionalidad de valoresValidos
    correct_result = 100
    input_user = '100'
    result = validador.obtener_int('-', input_user,valoresValidos=[1,2,100])
    if (result == correct_result):
        print('[+] Se valida funcionalidad de valoresValidos: 100 pertenece a [1,2,100]')
    else: 
        raise Exception('[x] ERROR al validar funcionalidad de valoresValidos: 100 pertenece a [1,2,100]')
    # 4. Se verifca funcionalidad de valoresValidos
    correct_result = False
    input_user = '100'
    result = validador.obtener_int('-', input_user,valoresValidos=[1,2])
    if (result == correct_result):
        print('[+] Se valida funcionalidad de valoresValidos: 100 no pertenece a [1,2]')
    else: 
        raise Exception('[x] ERROR al validar funcionalidad de valoresValidos: 100 no pertenece a [1,2]')

def test_obtener_tipo_topologia():
    print('\nfuncion: validador.obtener_tipo_topologia')
    valores = [{'correct_result':'lineal','input_user':1}, 
                {'correct_result':'malla','input_user':2},
                {'correct_result':'arbol','input_user':3},
                {'correct_result':'anillo','input_user':4},
                {'correct_result':'bus','input_user':5}]
    for valor in valores:
        try:
            result = validador.obtener_tipo_topologia(valor['input_user'])
            if (result == valor['correct_result']):
                print('[+] Se valida opcion '+str(valor['input_user'])+' -> '+valor['correct_result'])
            else:
                raise Exception('[x] ERROR al validar opcion '+str(valor['input_user'])+' -> '+valor['correct_result']+': se obtiene '+str(result))

        except InputException as inputException:
            raise Exception('[x] ERROR al validar opcion '+str(valor['input_user'])+' -> '+valor['correct_result']+': se obtiene InputException')

def test_obtener_infraestructura():
    print('\nfuncion: validador.obtener_infraestructura')
    valores = [{'inputInfraestructura':2,'inputAz':'1001,1002', 'correct_result': {'infraestructura': 'OpenStack', 'az': ['1001','1002'] }}, 
                {'inputInfraestructura':2,'inputAz':'1002,1003', 'correct_result': {'infraestructura': 'OpenStack', 'az': ['1002','1003'] }},
                {'inputInfraestructura':2,'inputAz':'1001,1003', 'correct_result': {'infraestructura': 'OpenStack', 'az': ['1001','1003'] }},
                {'inputInfraestructura':2,'inputAz':'1001,1002,1003', 'correct_result': {'infraestructura': 'OpenStack', 'az': ['1001','1002','1003'] }},
                {'inputInfraestructura':2,'inputAz':'1001', 'correct_result': {'infraestructura': 'OpenStack', 'az': ['1001'] }},
                {'inputInfraestructura':2,'inputAz':'1002', 'correct_result': {'infraestructura': 'OpenStack', 'az': ['1002'] }},
                {'inputInfraestructura':2,'inputAz':'1003', 'correct_result': {'infraestructura': 'OpenStack', 'az': ['1003'] }},
                {'inputInfraestructura':1,'inputAz':'1,2', 'correct_result': {'infraestructura': 'Linux Cluster', 'az': ['1', '2'] }},
                {'inputInfraestructura':1,'inputAz':'2,3', 'correct_result': {'infraestructura': 'Linux Cluster', 'az': ['2', '3'] }},
                {'inputInfraestructura':1,'inputAz':'1,3', 'correct_result': {'infraestructura': 'Linux Cluster', 'az': ['1', '3'] }},
                {'inputInfraestructura':1,'inputAz':'1,2,3', 'correct_result': {'infraestructura': 'Linux Cluster', 'az': ['1', '2', '3'] }},
                {'inputInfraestructura':1,'inputAz':'1', 'correct_result': {'infraestructura': 'Linux Cluster', 'az': ['1'] }},
                {'inputInfraestructura':1,'inputAz':'2', 'correct_result': {'infraestructura': 'Linux Cluster', 'az': ['2'] }},
                {'inputInfraestructura':1,'inputAz':'3', 'correct_result': {'infraestructura': 'Linux Cluster', 'az': ['3'] }},]
    for valor in valores:
        try:
            result = validador.obtener_infraestructura('-', valor['inputInfraestructura'], valor['inputAz'])
            if (result == valor['correct_result']):
                print('[+] Se valida infraestructura('+str(valor['inputInfraestructura'])+')->az('+str(valor['inputAz'])+') -> '+str(valor['correct_result']))
            else:
                raise Exception('[x] ERROR al validar opcion infraestructura('+str(valor['inputInfraestructura'])+')->az('+str(valor['inputAz'])+') -> '+str(valor['correct_result'])+': se obtiene '+str(result))

        except InputException as inputException:
            raise Exception('[x] ERROR al validar opcion infraestructura('+str(valor['inputInfraestructura'])+')->az('+str(valor['inputAz'])+') -> '+str(valor['correct_result'])+': se obtiene InputException')

def test_conectar_internet():
    print('\nfuncion: validador.conectar_internet')
    # 1 -> True
    try:
        inputTest = 1
        correct_result = True
        result = validador.conectar_internet(inputTest)
        if (result == correct_result):
            print('[+] Se valida input('+str(inputTest)+') -> '+str(correct_result))
        else:
            raise Exception('[x] ERROR al validar input('+str(inputTest)+') -> '+str(correct_result)+': se obtiene '+str(result))
    except InputException as inputException:
        raise Exception('[x] ERROR al validar input('+str(inputTest)+') -> '+str(correct_result)+': se obtiene InputException')
    # 2 -> False
    try:
        inputTest = 2
        correct_result = False
        result = validador.conectar_internet(inputTest)
        if (result == correct_result):
            print('[+] Se valida input('+str(inputTest)+') -> '+str(correct_result))
        else:
            raise Exception('[x] ERROR al validar input('+str(inputTest)+') -> '+str(correct_result)+': se obtiene '+str(result))
    except InputException as inputException:
        raise Exception('[x] ERROR al validar input('+str(inputTest)+') -> '+str(correct_result)+': se obtiene InputException')
    
def test_obtener_numero_vcpus():
    print('\nfuncion: validador.obtener_numero_vcpus')
    for inputTest in [1,2,4,8]:
        try:
            correct_result = inputTest
            result = validador.obtener_numero_vcpus(inputTest)
            if (result == correct_result):
                print('[+] Se valida input('+str(inputTest)+') -> '+str(correct_result))
            else:
                raise Exception('[x] ERROR al validar input('+str(inputTest)+') -> '+str(correct_result)+': se obtiene '+str(result))
        except InputException as inputException:
            raise Exception('[x] ERROR al validar input('+str(inputTest)+') -> '+str(correct_result)+': se obtiene InputException')

def test_obtener_memoria():
    print('\nfuncion: validador.obtener_memoria')
    for inputTest in [1,2,4,8]:
        try:
            correct_result = inputTest
            result = validador.obtener_memoria(inputTest)
            if (result == correct_result):
                print('[+] Se valida input('+str(inputTest)+') -> '+str(correct_result))
            else:
                raise Exception('[x] ERROR al validar input('+str(inputTest)+') -> '+str(correct_result)+': se obtiene '+str(result))
        except InputException as inputException:
            raise Exception('[x] ERROR al validar input('+str(inputTest)+') -> '+str(correct_result)+': se obtiene InputException')

def test_obtener_fs():
    print('\nfuncion: validador.obtener_fs')
    # 1. copyonwrite
    try:
        inputTest = 1
        correct_result = { 'filesystem': 'CopyOnWrite' }
        result = validador.obtener_fs(inputTest)
        if (result == correct_result):
            print('[+] Se valida input('+str(inputTest)+') -> '+str(correct_result))
        else:
            raise Exception('[x] ERROR al validar input('+str(inputTest)+') -> '+str(correct_result)+': se obtiene '+str(result))
    except InputException as inputException:
        raise Exception('[x] ERROR al validar input('+str(inputTest)+') -> '+str(correct_result)+': se obtiene InputException')
    # 1. raw
    try:
        inputTest = 2
        sizeTest = 30
        correct_result = { 'filesystem': 'Raw', 'size': sizeTest}
        result = validador.obtener_fs(inputTest, sizeTest=sizeTest)
        if (result == correct_result):
            print('[+] Se valida input('+str(inputTest)+') -> '+str(correct_result))
        else:
            raise Exception('[x] ERROR al validar input('+str(inputTest)+') -> '+str(correct_result)+': se obtiene '+str(result))
    except InputException as inputException:
        raise Exception('[x] ERROR al validar input('+str(inputTest)+') -> '+str(correct_result)+': se obtiene InputException')

def test_obtener_imagen():
    print('\nfuncion: validador.obtener_imagen')
    for inputTest in range(1,4):
        try:
            correct_result = inputTest
            result = validador.obtener_imagen('-', inputTest)
            if (result == correct_result):
                print('[+] Se valida input('+str(inputTest)+') -> '+str(correct_result))
            else:
                raise Exception('[x] ERROR al validar input('+str(inputTest)+') -> '+str(correct_result)+': se obtiene '+str(result))
        except InputException as inputException:
            raise Exception('[x] ERROR al validar input('+str(inputTest)+') -> '+str(correct_result)+': se obtiene InputException')

def test_nueva_topologia():
    print('\nfuncion: validador.nueva_topologia')
    valuesTest = {
                    "nombre": "topologia1",
                    "tipo": "lineal",
                    "infraestructura": {
                        "infraestructura": "Linux Cluster",
                        "az": [
                            "1",
                            "2"
                        ]
                    },
                    "vms": [
                        {
                            "n_vcpus": 1,
                            "memoria": 2,
                            "filesystem": {
                                "filesystem": "CopyOnWrite"
                            },
                            "imagen_id": 1,
                            "internet": True,
                        },
                        {
                            "n_vcpus": 4,
                            "memoria": 4,
                            "filesystem": {
                                "filesystem": "Raw",
                                "size": 10
                            },
                            "imagen_id": 3,
                            "internet": True,
                        },
                        {
                            "n_vcpus": 8,
                            "memoria": 2,
                            "filesystem": {
                                "filesystem": "Raw",
                                "size": 50
                            },
                            "imagen_id": 3,
                            "internet": False,
                        }
                    ]
                }
    correct_result = {
                    "nombre": "topologia1",
                    "tipo": "lineal",
                    "infraestructura": {
                        "infraestructura": "Linux Cluster",
                        "az": [
                            "1",
                            "2"
                        ]
                    },
                    "vms": [
                        {
                            "n_vcpus": 1,
                            "memoria": 2,
                            "filesystem": {
                                "filesystem": "CopyOnWrite"
                            },
                            "imagen_id": 1,
                            "internet": True,
                        },
                        {
                            "n_vcpus": 4,
                            "memoria": 4,
                            "filesystem": {
                                "filesystem": "Raw",
                                "size": 10
                            },
                            "imagen_id": 3,
                            "internet": True,
                        },
                        {
                            "n_vcpus": 8,
                            "memoria": 2,
                            "filesystem": {
                                "filesystem": "Raw",
                                "size": 50
                            },
                            "imagen_id": 3,
                            "internet": False,
                        }
                    ]
                }
    result = validador.nueva_topologia('', '-', valuesTest)
    if (result == correct_result):
        print('[+] Se valida input('+str(valuesTest)+') -> '+str(correct_result))
    else:
        raise Exception('[x] ERROR al validar input('+str(valuesTest)+') -> '+str(correct_result)+': se obtiene '+str(result))
        
def test_importar_imagen():
    print('\nfuncion: validador.importar_imagen')
    # opcion 1
    try:
        inputTest = { 'opcion':1,
                    'nombre':'imagen.img',
                    'categoria':'server',
                    'ruta':'/ruta/imagen.img'  }
        correct_result =  { 'opcion':1,
                    'nombre':'imagen.img',
                    'categoria':'server',
                    'ruta':'/ruta/imagen.img'  }
        result = validador.importar_imagen(inputTest)
        if (result == correct_result):
            print('[+] Se valida input para la opcion1 ('+str(inputTest)+') -> '+str(correct_result))
        else:
            raise Exception('[x] ERROR al validar input para la opcion1 ('+str(inputTest)+') -> '+str(correct_result)+': se obtiene '+str(result))
    except InputException as inputException:
        raise Exception('[x] ERROR al validar input para la opcion1 ('+str(inputTest)+') -> '+str(correct_result)+': se obtiene InputException')
    # opcion 2
    try:
        inputTest = {   'opcion':2,
                    'nombre':'imagen2.img',
                    'categoria':'security',
                    'url':'drive.com/imagen.img'  }
        correct_result =  {   'opcion':2,
                    'nombre':'imagen2.img',
                    'categoria':'security',
                    'url':'drive.com/imagen.img'  }
        result = validador.importar_imagen(inputTest)
        if (result == correct_result):
            print('[+] Se valida para la opcion2 ('+str(inputTest)+') -> '+str(correct_result))
        else:
            raise Exception('[x] ERROR al validar input para la opcion2 ('+str(inputTest)+') -> '+str(correct_result)+': se obtiene '+str(result))
    except InputException as inputException:
        raise Exception('[x] ERROR al validar input para la opcion2 ('+str(inputTest)+') -> '+str(correct_result)+': se obtiene InputException')
    # opcion 2 con categoria: networking
    try:
        inputTest = {   'opcion':2,
                    'nombre':'imagen2.img',
                    'categoria':'networking',
                    'url':'drive.com/imagen.img'  }
        correct_result =  {   'opcion':2,
                    'nombre':'imagen2.img',
                    'categoria':'networking',
                    'url':'drive.com/imagen.img'  }
        result = validador.importar_imagen(inputTest)
        if (result == correct_result):
            print('[+] Se valida input para la opcion2 con categoria=networking ('+str(inputTest)+') -> '+str(correct_result))
        else:
            raise Exception('[x] ERROR al validar input para la opcion2 con categoria=networking ('+str(inputTest)+') -> '+str(correct_result)+': se obtiene '+str(result))
    except InputException as inputException:
        raise Exception('[x] ERROR al validar input para la opcion2 con categoria=networking ('+str(inputTest)+') -> '+str(correct_result)+': se obtiene InputException')
    # categoria invalida
    try:
        inputTest = { 'opcion':1,
                    'nombre':'imagen.img',
                    'categoria':'aaaaaaaaaaa',
                    'ruta':'/ruta/imagen.img'  }
        result = validador.importar_imagen(inputTest)
        if (result):
            raise Exception('[x] ERROR, se ingreso una categoria invalida e igual se recibio un resultado: se obtiene '+str(result))
    except InputException as inputException:
        print('[+] Se verifica que se ingresa una categoria invalida: se obtiene InputException')

def test_agregar_nodo():
    print('\nfuncion: validador.agregar_nodo')
    valuesTest =  {
            'id_topologia': 1,
            'n_vcpus': 2,
            'memoria': 4,
            'filesystem': {"filesystem": "CopyOnWrite"},
            'imagen_id': 1,
            'internet': True
        }
    correct_result =  {
            'id_topologia': 1,
            'n_vcpus': 2,
            'memoria': 4,
            'filesystem': {"filesystem": "CopyOnWrite"},
            'imagen_id': 1,
            'internet': True
        }
    result = validador.agregar_nodo('-', valuesTest)
    if (result == correct_result):
        print('[+] Se valida input('+str(valuesTest)+') -> '+str(correct_result))
    else:
        raise Exception('[x] ERROR al validar input('+str(valuesTest)+') -> '+str(correct_result)+': se obtiene '+str(result))

def test_aumentar_slice():
    print('\nfuncion: validador.aumentar_slice')
    # combinacion 1
    inputTest =  '1,2,3'
    correct_result =  ['1', '2', '3']
    result = validador.aumentar_slice('-', ['1', '2', '3'], inputTest)
    if (result == correct_result):
        print('[+] Se valida input('+str(inputTest)+') -> '+str(correct_result))
    else:
        raise Exception('[x] ERROR al validar input('+str(inputTest)+') -> '+str(correct_result)+': se obtiene '+str(result))
    # combinacion 1
    inputTest =  '1,2'
    correct_result =  ['1', '2']
    result = validador.aumentar_slice('-', ['1', '2', '3'], inputTest)
    if (result == correct_result):
        print('[+] Se valida input('+str(inputTest)+') -> '+str(correct_result))
    else:
        raise Exception('[x] ERROR al validar input('+str(inputTest)+') -> '+str(correct_result)+': se obtiene '+str(result))
    # combinacion 1
    inputTest =  '2'
    correct_result =  ['2']
    result = validador.aumentar_slice('-', ['1', '2', '3'], inputTest)
    if (result == correct_result):
        print('[+] Se valida input('+str(inputTest)+') -> '+str(correct_result))
    else:
        raise Exception('[x] ERROR al validar input('+str(inputTest)+') -> '+str(correct_result)+': se obtiene '+str(result))
    # input no valido
    inputTest =  '1,2,3.6'
    try:
        result = validador.aumentar_slice('-', ['1', '2', '3'], inputTest)
        if (result):
            raise Exception('[x] ERROR, se ingreso una ID invalido e igual se recibio un resultado: se obtiene '+str(result))
    except InputException as inputException:
        print('[+] Se verifica que se ingresa un ID invalido: se obtiene InputException')

if __name__ == '__main__':
    validador = ValidadorTest()
    
    # modulo: validador
    print('\nSe inician las pruebas...')
    print('\nmodulo: validador\n')
    test_obtener_int()
    test_obtener_tipo_topologia()
    test_obtener_infraestructura()
    test_conectar_internet()
    test_obtener_numero_vcpus()
    test_obtener_memoria()
    test_obtener_fs()
    test_obtener_imagen()
    test_nueva_topologia()
    test_importar_imagen()
    test_agregar_nodo()
    test_aumentar_slice()