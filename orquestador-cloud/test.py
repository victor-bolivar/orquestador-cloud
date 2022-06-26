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
        print('[x] ERROR al validar un entero')
    # 2. Se verifca funcionalidad de maxValor,minValor
    correct_result = 100
    input_user = '100'
    result = validador.obtener_int('-', input_user, minValor=50, maxValor=200)
    if (result == correct_result):
        print('[+] Se valida funcionalidad de maxValor,minValor: se cumple 50<=100<=200')
    else: 
        print('[x] ERROR al validar funcionalidad de maxValor,minValor (50<=100<=200)')
    # 3. Se verifca funcionalidad de maxValor,minValor
    correct_result = False
    input_user = '500'
    result = validador.obtener_int('-', input_user, minValor=50, maxValor=200)
    if (result == correct_result):
        print('[+] Se valida funcionalidad de maxValor,minValor: se obtiene False al evaluar 500<=200')
    else: 
        print('[x] ERROR al validar funcionalidad de maxValor,minValor: no se obtiene False al evaluar 500<=200')
    # 4. Se verifca funcionalidad de valoresValidos
    correct_result = 100
    input_user = '100'
    result = validador.obtener_int('-', input_user,valoresValidos=[1,2,100])
    if (result == correct_result):
        print('[+] Se valida funcionalidad de valoresValidos: 100 pertenece a [1,2,100]')
    else: 
        print('[x] ERROR al validar funcionalidad de valoresValidos: 100 pertenece a [1,2,100]')
    # 4. Se verifca funcionalidad de valoresValidos
    correct_result = False
    input_user = '100'
    result = validador.obtener_int('-', input_user,valoresValidos=[1,2])
    if (result == correct_result):
        print('[+] Se valida funcionalidad de valoresValidos: 100 no pertenece a [1,2]')
    else: 
        print('[x] ERROR al validar funcionalidad de valoresValidos: 100 no pertenece a [1,2]')

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
                print('[x] ERROR al validar opcion '+str(valor['input_user'])+' -> '+valor['correct_result']+': se obtiene '+str(result))

        except InputException as inputException:
            print('[x] ERROR al validar opcion '+str(valor['input_user'])+' -> '+valor['correct_result']+': se obtiene InputException')

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
                print('[x] ERROR al validar opcion infraestructura('+str(valor['inputInfraestructura'])+')->az('+str(valor['inputAz'])+') -> '+str(valor['correct_result'])+': se obtiene '+str(result))

        except InputException as inputException:
            print('[x] ERROR al validar opcion infraestructura('+str(valor['inputInfraestructura'])+')->az('+str(valor['inputAz'])+') -> '+str(valor['correct_result'])+': se obtiene InputException')


if __name__ == '__main__':
    validador = ValidadorTest()
    
    # modulo: validador
    print('\nSe inician las pruebas...')
    print('\nmodulo: validador\n')
    test_obtener_int()
    test_obtener_tipo_topologia()
    test_obtener_infraestructura()