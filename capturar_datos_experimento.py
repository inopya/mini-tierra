#!/usr/bin/python
# -*- coding: utf-8 -*-


#       _\|/_   A ver..., ¿que tenemos por aqui?
#       (O-O)        
# ---oOO-(_)-OOo---------------------------------
 
 
##########################################################
# ****************************************************** #
# *          LABORATORIO PARA PRINCIPIANTES            * #
# *  Utilidad graficas de ficheros diarios de datos    * #
# *          Autor:  Eulogio López Cayuela             * #
# *                                                    * #
# *     Captura de datos  v1.0   Fecha: 20/08/2018     * #
# ****************************************************** #
##########################################################

'''
    Utilidad que nos permite recopilar datos desde Arduino
    u otro dispositivo que se comunique por puerto serie
    para su almacenamiento y representacion desde python.
    Mantendra activa una representacion grafica de los mismos
    y permitira la interaccion mediante un bot de telegram.
    La distribucion, el numero y el color de las graficas se
    hace de forma automatica en funcion del numero de datos
    que recibe, aunque es posible cambiar el aspecto de forma manual.
    
    Entre los datos a configurar por el usuario esta el 'numero de sensores'
    que facilitará el posicionamiento de los graficos. -- Seccion principal LINEA 1189 --
    Veras que con una pequeña modificacion se puede hacer que el programa automaticamente
    se adapte a los datos recibidos, pero se ha optado por esta solucion por comodidad.
    Asi indicando el numero de sensores y los nombres de estos, tendremos siempre los
    graficos bien etiquetados.


    SOLO PARA PYTHON 3.x

    algunas bibliotecas que quizas necesites instalar:

    (si no puedes instalar directamente intentalo mejor con 'sudo'
    y si no te funciona con 'pip install' intentalo con 'pip3 install')

    python -m pip install --upgrade pip setuptools wheel
    python -m pip install pyserial
    python -m pip install matplotlib
    python -m pip install numpy
    python -m pip install python-telegram-bot --upgrade

    Si lo vas a ejecutar desde un ordenador con windows
    quizas esta pagina te facilite la vida para instalar paquetes
    https://www.lfd.uci.edu/~gohlke/pythonlibs/


'''




#--------------------------------------------------------
# IMPORTACION DE MODULOS
#--------------------------------------------------------

# TELEGRAM
import telegram
from telegram import ReplyKeyboardMarkup
from telegram.error import NetworkError, Unauthorized


# ACCESO A DATOS EN SERVIDORES (usado por telegram)
import json 
import requests

### EXPRESIONES REGULARES
##import re # lo usamos para verificar los email  (sin uso en este montaje)


# FILTRADO DE ERRORES
#matplotlib (al menos la version que uso) me genera algunos mensajes de advertencia que prefiero no ver
import warnings
warnings.filterwarnings("ignore")

# TIEMPOS, FECHAS
from time import sleep      #pausas...
import datetime

# EMAIL
import smtplib
# librerias  para construir el mensaje
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 
# librerias para adjuntar archivos
from email.mime.base import MIMEBase
from email import encoders 


#INTERACTUAR CON EL SISTEMA OPERATIVO
    
import sys              #Conocer el tipo de sistema operativo
import time             #manejo de funciones de tiempo (fechas, horas, pausas...)
import os               #manejo de funciones del sistema operativo 
from os import walk     #funciones para movernos por directorios


# ACCESO AL PUERTO SERIE (para comunicarse con Arduino)
import serial  


# REPRESENTACION GRAFICA DE DATOS
import matplotlib                               #funcionalidad para representacion grafica de datos
import matplotlib.pyplot as plt                 #por comodidad al llamar esta funcionalidad
from matplotlib.ticker import MultipleLocator   #para crear leyendas en los graficos
from matplotlib import style
import matplotlib.colors as mcolors             #para manejar los colores de matplotlib


# FUNCIONES MATEMATICAS AVANZADAS
import numpy as np
import math


# 'SERIALIZACION' DE OBJETOS (para manejar el salvado de datos)
try:  
    import cPickle as pickle  
except ImportError:  
    import pickle  



#====================================================================================================
#  INICIO DEL BLOQUE DEFINICION DE CONSTANTES Y VARIABLES GLOBALES PARA EL PROGRAMA 
#====================================================================================================


'''***********************************************************************************************'''
'''***********************************************************************************************'''
'''***********************************************************************************************'''

#    IMPORTANTE, DATOS A CONFIGURAR POR EL USUARIO    #

'''***********************************************************************************************'''

#DATOS DEL SERVIDOR DE CORREO PARA REALIZAR LOS ENVIOS
#ojo, aqui estaran visibles la direccion y la contraseña :(  (Recuerdalo a la hora de pasar el codigo a alguien)
#Las cuentas de gmail deberan configurarse para que admitan "dispositivos no seguros" 

SMTP_CORREO_ENVIOS =  'smtp.yandex.com'
EMAIL_CORREO_ENVIOS = 'xxxxxxx@yandex.com'
PASS_CORREO_ENVIOS =  'xxxxxxx'
REMITENTE_CORREO_ENVIOS = 'xxxxxxx@yandex.com'                #yandex no permite otro remitente que no sea la direccion de salida
                                                              #si usais gmail como smtp, podeis poner una cadena de texto a vuestro gusto :)

#lista de direcciones de correo a la que se enviaran los datos del experimento. Necesaria al menos una direccion.
lista_correo_experimento = ['sorbasdigital@hotmail.com']      #quitar esta y poner la vuestra


#CLAVE para la API de telegram (token del bot)
TOKEN = "57887:FrG4XvA_5DMKHRXj" # quitar este y poner el de vuestro bot


# Definimos la id del que sera el usuarios administrador y que dispondra de derechos de uso completo
# (podemos definir otros usuarios que no tengan acceso total)

ADMIN_USER = None  #None: todos los que conectan pueden realizar:   - el envio de correo a la lista de autorizados
                   #                                                - el salvado manual de datos
                   #                                                - el borrado de datos
                   #                                                - Parada remota de la toma e datos
                   #Si establecemos un numero ID de telegram, solo el usuario con ese numero ID puede realizar estos comandos


ID_ESTACION_BIO = "INOPYA"   # este ID se incorpora a los mensajes de informacion
                             #y a las muestras de datos del fichero txt (sustituirla por algo personal)

TIEMPO_ENTRE_MUESTRAS = 60 # tiempo en segundos. Por defecto 60, un minuto


#seccion para rutas y nombres de ficheros 
RUTA_BACKUP = 'backup/'                         #recuerda crear la subcarpeta que desees usar como destino

FICHERO_DATOS_EXPERIMENTO =     'experimento_minitierra.dat'
FICHERO_DATOS_DIA_EN_CURSO =    'minitierra_dia_en_curso.dat'
FICHERO_TXT_EXPERIMENTO =       'experimento_minitierra.txt'
FICHERO_GRAFICA_EXPERIMENTO =   'experimento_minitierra.png'

'''***********************************************************************************************'''
'''***********************************************************************************************'''
'''***********************************************************************************************'''


#URL de la API de TELEGRAM
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


update_id = None

user_keyboard = [['/info','/fig'],['/email', '/txt'],['/save','/ayuda'],['/stop'],['/deleteOld','/deleteNew']]
user_keyboard_markup = ReplyKeyboardMarkup(user_keyboard, one_time_keyboard=True)

""" poner en marcha el bot """
telegram_bot_experimento_bio = telegram.Bot(TOKEN)

#comandos a mostrar al pedir '/ayuda'
listaComandos = ["/ayuda - Mostrar esta Ayuda", \
                 "/email - envia datos completos por email",\
                 "/info - Mostrar datos actuales", \
                 "/txt - envia datos completos a telegram", \
                 "/fig - Grafico de Evolucion",\
                 "/deleteOld - Borra los 15 primeros datos",\
                 "/deleteNew - Borra los 15 ultimos datos",\
                 "/stop - Finaliza el experimento",\
                 "/save - Realiza una copia de seguridad","\n"]


#bucle para generar el texto encadenando todos los comandos de ayuda.
#Para el mensaje que se envia por telegram al pedir '/ayuda'
listaComandosTxt = ""
for comando in listaComandos:
    listaComandosTxt += comando+"\n"


#Ruta absoluta en la que se encuentra el script. Util apra las llamadas desde el inicio del sistema
RUTA_PROGRAMA = os.path.dirname(os.path.abspath(__file__)) +'/'
NOMBRE_SCRIPT_EN_EJECUCION = os.path.basename(__file__)


print ("==================================================")
print ("\nRuta ABSOUTA DEL PROGRAMA:\n", RUTA_PROGRAMA)
print ("\nNombre del fichero en ejecucion:\n", NOMBRE_SCRIPT_EN_EJECUCION)
print ("\n==================================================\n\n")

#control de existencia de las carpetas de trabajo necesarias
ruta1 = RUTA_PROGRAMA + RUTA_BACKUP[:-1]
if not os.path.exists(ruta1):
    os.makedirs(ruta1)
    print("Error no existia la carpeta backup, pero la he creado")
ruta2 = RUTA_PROGRAMA + RUTA_BACKUP + "diarios"
if not os.path.exists(ruta2):
    os.makedirs(ruta2)
    print("Error no existia la carpeta backup/diarios , pero la he creado")

   
SerialDelay = 0.5                   #tiempo entre llamadas del puerto (en segundos), para que pueda reaccionar.
                                    #No usar tiempos inferiores a 0.25 segundos 

FLAG_run = True                     #por si queremos parar el experimento mediante un comando telegram 
FLAG_momento_salvado_datos = True   #para controlar el momento de salvado automatico de los datos
FLAG_backup_datos_Enabled = True    #para permitir (o no) el salvado automatico y periodico de los datos

FLAG_reinicio_Arduino = True        #control de si es la primera vez que estamos intentando acceder a arduino
                                    #para evitar errores por variables que aun no se hayan podido cargar

FLAG_buscandoConexion = True        #bandera apra el control de reconexiones
                                    #en caso de que se pierda la comunicacion con arduino

FLAG_estacion_online = True         #podemos desactivala si no vamos a hacer uso de telegram y correo

FLAG_enviar_PNG = False             #controla el proceso de envio de grafica al usuario
FLAG_enviar_TXT = False             #controla el proceso de envio de fichero de datos al usuario

FLAG_delete_old = False             #control de borrado de los primeros datos tomados
FLAG_delete_new = False             #control de borrado de los ultimos datos tomados

FLAG_pruebas = False                #Para hacer pruebas con telegram (sin uso)


################   " <---------- METADATOS -------->  <---------- SENSORES ----------------------> "
cabeceraTXTdatos = "n muestra\tESTACION\tFECHA\tHORA\tTemp_int\tHumedad\tPH\tCO2\tPresion\tTemp_ext"


minuto_adquisicion_datos = -1       # para forzar lectura y preparacion de datos justo al iniciar el programa, si no da error 
minuto_dibujar_grafica = -1
minuto_error_grafica = -1
minuto_error_arduino  = -1

INTERVALO_BACKUP = 10               #intervalo en minutos para copias de seguridad 

VELOCIDAD_PUERTO_SERIE = 115200


#variables globales para almacenar los datos recogidos de arduino
valor_sensores_Now = []
ultimos_valores_validos = []


#esta lista es muy importante ya que guardaran los datos de las muestras
# para registro y para dibujar de la grafica
lista_Datos_Experimento = []
lista_Datos_SOLO_dia_en_curso = []

#----------------------------------------------------------------------------------------------------
#  FIN DEL BLOQUE DEFINICION DE VARIABLES GLOBALES
#----------------------------------------------------------------------------------------------------



#====================================================================================================
# INICIO BLOQUE DE DEFINICION DE CLASES
#====================================================================================================

class RelojLOCAL:
    '''
    Classe para el control personal de los tiempos.
    crea un reloj con la hora local del sistema en el que corre el sistema de registro de datos
    El reloj adquiere la fecha/hora actuales al iniciarse, y
    OJO, solo se actualiza con el metodo update()
    y hasta ese momento mantiene el anterior registro de fecha/hora
    '''
    def __init__(self):
        self.update()
        
    def update(self):        
        #self.tiempo_gmt = time.strftime("%Y_%m_%d-%H:%M:%S", time.gmtime(time.time()))   #hora gmt
        self.tiempo_str = time.strftime("%Y/%m/%d-%H:%M:%S", time.localtime(time.time())) #hora local
        self.tiempo_str2 = time.strftime("%Y_%m_%d-%H_%M_%S", time.localtime(time.time())) #hora local
        self.tiempo = time.time() #float del tiempo GMT
        self.fechayhora = self.tiempo_str[:]

        self.fecha = self.tiempo_str[0:10]
        self.fecha2 = self.tiempo_str2[0:10]
        self.reloj = self.tiempo_str[11:]

        self.year = self.tiempo_str[0:4]
        self.mes = self.tiempo_str[5:7]
        self.dia = self.tiempo_str[8:10]

        self.hora = self.tiempo_str[11:13]
        self.minuto = self.tiempo_str[14:16]
        self.segundo = self.tiempo_str[17:19]

                
#----------------------------------------------------------------------------------------------------
# FIN BLOQUE DE DEFINICION DE CLASES
#----------------------------------------------------------------------------------------------------



#====================================================================================================
# INICIO DEL BLOQUE DE DEFINICION DE FUNCIONES
#====================================================================================================

# mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
# FUNCIONES TELERAM
# mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm


def get_url(url):
    '''
    Funcion de apoyo a la recogida de telegramas,
    Recoge el contenido desde la url de telegram
    '''
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------

def send_message(text, chat_id):
    '''
    Funcion para enviar telergamas atraves de la API
    '''
    try:
        url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
        #print("url >> ",url)
        get_url(url)
    except:
        print("ERROR de envio")

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------  

def atenderTelegramas(bot):
    '''
    Funcion principal de la gestion de telegramas.
    Los atiende y procesa, ejecutando aquellos que son ordenes directas.
    Solicita la 'ayuda' de otras funciones para aquellos comandos
    complejos que contiene parametros
    '''
    global text, chat_id, chat_time, comando, chat_user_name
    global FLAG_enviar_PNG, FLAG_pruebas, FLAG_enviar_TXT, FLAG_run
    global FLAG_delete_old, FLAG_delete_new

    global update_id
    chat_id = 0
    try:    
        # Request updates after the last update_id
        for update in bot.get_updates(offset=update_id, timeout=0): #timeout=5, si nos da problemas con internet lento
            update_id = update.update_id +1

            if update.message:                              # porque se podrian recibir updates sin mensaje...
                comando = update.message.text               #MENSAJE_RECIBIDO
                chat_time = update.message.date
                user = update.message.from_user             #USER_FULL
                chat_id = int(update.message.from_user.id)
                chat_user_name = user.first_name            #USER_REAL_NAME
                usuario = chat_user_name
                            
                try:
                    # para DEBUG, imprimimos lo que va llegando
                    print (str(chat_time) + " >>> " + str(chat_id) +": " + usuario + " --> " + comando)
                    
                    if update.message.entities[0].type == "bot_command" and update.message.text == "/start":
                        update.message.reply_text("Bienvenido a Experimento Bio v1.0", reply_markup=user_keyboard_markup)
                                            
                    # ===============   INTERPRETAR LOS COMANDOS QUE LLEGAN Y ACTUAR EN CONSECUENCIA   ===============
                    
                    if comando == "/send" and (chat_id == ADMIN_USER or ADMIN_USER == None):  #decidir quien puede enviar correos
                        send_message("procesando peticion...", chat_id)
                        nombreRutaConExtension = RUTA_PROGRAMA + RUTA_BACKUP + FICHERO_TXT_EXPERIMENTO
                        status1 = convertir_Datos_to_TXT(lista_Datos_Experimento, nombreRutaConExtension, \
                                                         cabecera=cabeceraTXTdatos)
                        status2 = enviarEmail(nombreRutaConExtension)
                        if(status1==True and status2==True):
                            send_message("EMAIL enviado correctamente", chat_id)
                        else:
                            send_message("ERROR al enviar Email. Intentalo mas tarde", chat_id)
                        return
          
                    if comando == "/save" and (chat_id == ADMIN_USER or ADMIN_USER == None):  #solo el administrador puede forzar el salvado de datos no programado
                        nombre_con_ruta = RUTA_PROGRAMA + RUTA_BACKUP + FICHERO_DATOS_EXPERIMENTO
                        status1 = salvar_Backup_datos(lista_Datos_Experimento, nombre_con_ruta)
                        nombreCompleto = RUTA_PROGRAMA + RUTA_BACKUP + FICHERO_TXT_EXPERIMENTO
                        status2 = convertir_Datos_to_TXT(lista_Datos_Experimento, nombreCompleto, \
                                                         cabecera=cabeceraTXTdatos)
                        plt.savefig(RUTA_PROGRAMA + RUTA_BACKUP + FICHERO_GRAFICA_EXPERIMENTO)

                        if status1==True and status2==True:
                            send_message("OK, Copia de seguridad realizada", chat_id)
                        else:
                            send_message("ERROR. No se pudo realizar copia de seguridad", chat_id)
                        return

                    # Lista de comandos para usuarios basicos (clientes)           
                    if comando == "/ayuda":
                        send_message (listaComandosTxt, chat_id)
                        return
                    
                    if comando == "/info":
                        if(len(valor_sensores_Now)< 6):
                            return
                        send_message ("============================\n" +
                                      "  ESTACION ID: <<" + ID_ESTACION_BIO + ">>\n"
                                      "  HORARIO  UTC/GMT +1\n" +
                                      "  " + reloj.fecha + "  " + reloj.reloj + "\n" +
                                      "============================\n\n" +
                                      "VALORES ACTUALES: \n\n" +
                                      " Temp_int:   " + str(valor_sensores_Now[0]) + " ºC\n" +
                                      " Humedad:   " + str(valor_sensores_Now[1]) + " %\n" +
                                      " PH:   " + str(valor_sensores_Now[2])+"\n" +
                                      " CO2:   " + str(valor_sensores_Now[3]) + " ppm\n" +
                                      " Presion:   " + str(valor_sensores_Now[4]) + " \n" +
                                      " Temp_ext:   " + str(valor_sensores_Now[5]) + " \n"                                       
                                      , chat_id)
                        
                        return

                    if comando == "/stop" and (chat_id == ADMIN_USER or ADMIN_USER == None):
                        FLAG_run = False
                        FLAG_enviar_TXT = True  #Activamos un ultimo envio de datos al usuario por si acaso
                        FLAG_enviar_PNG = True  #activamos tambien el envio de la grafica
                        return
                    
                    if comando == "/fig":
                        FLAG_enviar_PNG = True
                        return 
                    
                    if comando == "/txt":
                        FLAG_enviar_TXT = True
                        return
                     
                    if comando == "/deleteOld" and (chat_id == ADMIN_USER or ADMIN_USER == None):
                        #FLAG_delete_old = True  #desactivamos por precaucion
                        return
                    if comando == "/deleteNew" and (chat_id == ADMIN_USER or ADMIN_USER == None):
                        FLAG_delete_new = True  #desactivamos por precaucion
                        return                    
                except:
                    print ("----- ERROR ATENDIENDO TELEGRAMAS ----------------------")                      
                if chat_id != 0:
                    #ante cualquier comando desconocido devolvemos 'ok', para despistar a los que intenten 'probar suerte'
                    send_message ("OK" ,chat_id)  
        
    except:
        pass
    
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
    
# mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
# ENVIO DE EMAIL
# mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm

def enviarEmail(nombreRutaConExtension):
    '''
    Funcion para realizar los envio de los datos del experimento por email
    a los clientes suscritos
    Aqui llega la ruta + nombre del fichero registro + extrension *.txt
    Entre las tareas a realizar extraemos solo el "nombre.txt"
    para usarlo como texto en el asunto del mensaje
    '''

    global lista_correo_experimento
    #Esta lista contiene objetos tipo cartero,
    #con la id de telegram  .user  y las direcciones de correo .email
    #desgranamos la lista para hacer una nueva lista de solo direcciones de email
    
    destinatarios = []
    for email in lista_correo_experimento:
        destinatarios.append(email)
        
    nombreRutaTxt= nombreRutaConExtension
    soloNombreTxt = nombreRutaTxt.split("/")[-1]

    #el mail sale desde el correo xxxxx@xxxx.xxx (definimos el correo del remitente)
    remitente = REMITENTE_CORREO_ENVIOS
    # Definimos los detalles del servisor email SMTP
    smtp_server = SMTP_CORREO_ENVIOS
    smtp_user   = EMAIL_CORREO_ENVIOS
    smtp_pass   = PASS_CORREO_ENVIOS

    try: 
        # Construimos el mail
        msg = MIMEMultipart() 
        msg['Bcc'] = ", ".join(destinatarios)
        msg['From'] = remitente
        msg['Subject'] = 'Registro Datos   >>> ' + soloNombreTxt

        #cuerpo del mensaje en HTML
        msg.attach(MIMEText('<h1>Registro de datos de Experimento Bio</h1><p>','html'))

        ##cargamos el archivo a adjuntar
        fp = open(nombreRutaTxt,'rb')
        adjunto = MIMEBase('multipart', 'encrypted')
        #lo insertamos en una variable
        adjunto.set_payload(fp.read()) 
        fp.close()  
        #lo encriptamos en base64 para enviarlo
        encoders.encode_base64(adjunto) 
        #agregamos una cabecera e indicamos el nombre del archivo
        adjunto.add_header('Content-Disposition', 'attachment', filename=soloNombreTxt) #
        #adjuntamos al mensaje
        msg.attach(adjunto) 

        # inicializamos el stmp para hacer el envio
        server = smtplib.SMTP(smtp_server)
        server.starttls() 

        #logeamos con los datos ya seteamos en la parte superior
        server.login(smtp_user,smtp_pass)

        #realizamos los envios a los suscriptores
        server.sendmail(remitente, destinatarios, msg.as_string())
        
        #apagamos conexion stmp
        server.quit()
        print ("DEBUG >>>   CORREOS ENVIADOS")
        return True

    except Exception as e:
        print ("---------------------------")
        print ("ERROR AL ENVIAR E-MAIL")
        print(e)
        return False

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------
    
# mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
# FUNCIONES ARDUINO / SERIAL
# mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm

def detectarPuertoArduino():   #version mejorada 2018
    '''
    Funcion para facilitar la deteccion del puerto Serie en distintos sistemas operativos
    Escanea los posibles puertos y retorna el nombre del puerto con el que consigue comunicarse
    '''

    #Reconocer el tipo de sistema operativo
    sistemaOperativo = sys.platform
    
    #Definir los prefijos de los posibles puertos serie disponibles tanto en linux como windows
    puertosWindows = ['COM']
    puertosLinux = ['/dev/ttyACM',  '/dev/ttyUSB', '/dev/ttyS', '/dev/ttyACA'] #'/dev/ttyAMA', Arduino Micro da problemas con este puerto
    
    puertoSerie = ''
    if (sistemaOperativo == 'linux' or sistemaOperativo == 'linux2'):
        listaPuertosSerie = puertosLinux
        index = 0
    else:
        listaPuertosSerie = puertosWindows
        index = 4  # Windows suele reservar los 3 primeros puertos. Cambiar este indice si no detectamos nada
        
    for sufijo in listaPuertosSerie:
        for n in range(index, 35):
            try:
                # intentar crear una instancia de Serial para 'dialogar' con ella
                nombrePuertoSerie = sufijo + '%d' %n
                print ("Probando... ", nombrePuertoSerie)
                #time.sleep(0.5)
                serialTest = serial.Serial(nombrePuertoSerie, VELOCIDAD_PUERTO_SERIE)
                serialTest.close()
                return nombrePuertoSerie

            except:
                pass
        
    return '' #si llegamos a este punto es que no hay Arduino disponible

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------  

def consultar_Arduino(PAUSA = 0.5):
    '''
    Funcion para acceso a ARDUINO y obtencion de datos en tiempo real   ---
    version mejorada para evitar errores de comunicacion
    ante eventuales fallos de la conexion.
    '''
    global arduinoSerialPort, FLAG_buscandoConexion

    try:
        arduinoSerialPort.flushInput() #eliminar posibles restos de lecturas anteriores
        arduinoSerialPort.flushOutput()#abortar comunicaciones salientes que puedan estar a medias

    except:
        print ("------------------------------------------------")
        print ("error borrando datos del puerto Serie de Arduino")
 
    try:
        #enviar comando para que ARDUINO reaccione. El prefijo b (byte) es opcional en python 2.x pero obligatorio en 3.x
        arduinoSerialPort.write(b'*')
        #pausa para que arduino tenga tiempo de reaccionar y dejar la informacion en el puerto Serie
        time.sleep(PAUSA)
        #revisar si hay datos en el puerto serie
        if (arduinoSerialPort.inWaiting()>0):  
            #leer una cadena desde el el puerto serie y 'despiojarla'
            linea_leida_de_Arduino = arduinoSerialPort.readline().strip()
            linea_leida_de_Arduino = linea_leida_de_Arduino.decode("utf-8")
            listaObtenidaDelinea = []
            try:
                listaObtenidaDelinea = linea_leida_de_Arduino.split("**")
                #los datos leidos de arduino son una cadena de texto. La partimos y convertimos a numeros decimales
                for n in range (len(listaObtenidaDelinea)):
                    listaObtenidaDelinea[n] = float(listaObtenidaDelinea[n])
                return  listaObtenidaDelinea #devolvemos los datos (La validez se comprueba en el lugar de llamada)
            except:
                print ("\n")
                print (linea_leida_de_Arduino, listaObtenidaDelinea)
                print ("\nError durante la adquisicion.\nDatos no validos, pidiendo una nueva muestra")
                print ("<<  Contactar con el administrador o tecnico de mantenimiento si el problema persiste  >>\n\n")
                #notificamos el problema de lectura de datos para que se tome otra muestra lo antes posible
                return None
    except:
        #si llegamos aqui es que se ha perdido la conexion con Arduino  :(
        print ("\n_______________________________________________")
        if FLAG_buscandoConexion == False:      #primera vez que llegamos aqui
            print ("\n == CONEXION PERDIDA == ")
            FLAG_buscandoConexion = True        #para no repetir el texto mientras se reestablece la conexion

        tiempoInicio = time.time()
        ActualTime = time.time()
        print ("    Reconectando...")
        while (ActualTime - tiempoInicio < 10): #Control del tiempo entre consultas de ARDUINO  :)
            arduinoSerialPort.close() #cerrar puerto anterior por seguridad
            puertoDetectado = detectarPuertoArduino() #detactamos automaticamente el puerto
            ActualTime = time.time()
            if (puertoDetectado != ''):
                arduinoSerialPort = serial.Serial(puertoDetectado, VELOCIDAD_PUERTO_SERIE) #usamos el puerto detectado
                print ("\n")
                FLAG_buscandoConexion = False
                print (" ** COMUNICACION REESTABLECIDA en "  + puertoDetectado + " ** \n")
                print (epochDate(time.time()))
                print ("_______________________________________________\n\n")
                break
    print ("Arduino sin datos disponibles")
    return None   # notificamos un problema de lectura de datos para que se intente tomar otra muestra lo antes posible

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------  
     
def epochDate(epoch):
    '''
    Funcion para convertir un tiempo epoch en fecha/hora 'humana'
    Usado para imprimir los tiempos que forman parte de los detalles de los telegramas y mensajes de consola
    '''
    fechaHora = time.strftime("%Y-%m-%d , %H:%M:%S", time.localtime(epoch))
    return fechaHora

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------  

# mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
# FUNCIONES CONTROL Y GESTION DE FICHEROS DE DATOS
# mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
   
def salvar_Backup_datos(informacion_para_salvar, nombre_con_ruta):
    ''' Salvado de datos que autogenera una copia con el mismo nombre recibido pero con extension BAK '''
    
    try:   
        ficheroDatos = open(nombre_con_ruta, "wb")
        pickle.dump(informacion_para_salvar, ficheroDatos, protocol=-1) # -1, seleccion automatica del más alto disponible  
        ficheroDatos.close()
        
        #CREACION DE COPIAS  .bak AUTOMATICAMENTE
        #separamos el nombre y la extenxion de la informacion que llega a la funcion
        longitud_extension = len(nombre_con_ruta.split(".")[-1])
        nombre_con_ruta_backup = nombre_con_ruta[:-longitud_extension] + "bak"
        ficheroDatos_backup = open(nombre_con_ruta_backup, "wb")
        pickle.dump(informacion_para_salvar, ficheroDatos_backup, protocol=-1) # -1, seleccion automatica del más alto disponible  
        ficheroDatos.close()
        return(True)

    except:
        print ("---------------------------")
        print ("Error Guardando backup >> ", nombre_con_ruta)

        return(False)                   
    
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------  

def cargar_datos_desde_fichero(nombre_con_ruta):
    ''' Recuperacion de los datos de backup desde fichero en los momentos de reinicio '''

    datos = []
    try:
        nombreDatosFile = nombre_con_ruta
        ficheroDatos = open(nombreDatosFile,"rb")
        datos = pickle.load(ficheroDatos)
        ficheroDatos.close()
        return True, datos
        
    except:
        print ("---------------------------")
        print ("error con la carga de registros de backup")
        return False , []

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------  

def ListaUnica (lista, destino):
    for n in range(len(lista)):
        if isinstance(lista[n],list):
            ListaUnica(lista[n], destino)
        else:
            destino.append(lista[n])
    return destino
    
#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------  

def convertir_Datos_to_TXT(datos, nombreDatosFile, cabecera=""):
    '''
    RECIBE UNA LISTA o UN EMPAQUETADO (una lista de listas) y el nombre con el que queremos guardar el TxT
    Funcion para la conversion de los datos de una serie de listas
    a un formato de texto plano separado en colunmas.
    Opcionalmente podemos indicar uan cabecera de texto apra dichos datos
    Esta sera informacion que se envia por email a los suscriptores
    '''
    #datos = lista simple  o bien lista de listas
    nombreFileSalida = nombreDatosFile

    numeroDatos = len(datos)

    outfile = open(nombreFileSalida, 'w') # Indicamos el valor 'w' para escritura.

    if cabecera != "": #si hay informacion de cabecera se añade antes de los datos para no numerar esa linea
        outfile.write(cabecera)
        outfile.write("\n\n")
        #y dejamos el fichero abierto para seguir escribiendo la informacion correspondiente a los datos

    if datos == []: #Si llega una lista vacia (que puede ser) se generarian errores,
                    #asi que añadimos una linea para informar de ello, cerramos el fichero y salimos
        outfile.write("\nNo hay informacion disponible\n")
        outfile.close()
        return (True)
    
    try:
        for x in range(len(datos)):
            lista_unica=[]
            indice = "00000"+ str(x)
            indice = indice[-5:]
            linea = indice + "\t"

            lista_unica = ListaUnica(datos[x], lista_unica)

            for elemento in lista_unica:
                if str(type(elemento))== "<class 'int'>" or str(type(elemento))== "<class 'float'>":
                    dato = float(elemento)
                    dato = "%.2f" % (dato)
                    linea += str(dato) + "\t"
                else:
                    linea += elemento + "\t"
            linea += "\n" 
            outfile.write(linea)
        outfile.close()
        return (True)

    except:
        print ("---------------------------")
        outfile.close()                         #Cerramos por si se quedo abierto
        outfile = open(nombreFileSalida, 'wb')  #Reabrimos nuevamente y escribimos un mensaje de error
        linea = "\n\nHubo un error en la conversion de datos\n\nContacte EXPERIMENTO BIO en telegram con el comando /DATA_ERROR_"+nombreDatosFile[:-4]+" y solicite los datos en formato RAW si lo desea \n" 
        outfile.write(linea)
        outfile.close()
        return (False)

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------  

# mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
# REPRESENTACION GRAFICA
# mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm

#generar lista con las posiciones de los graficos
def generar_posicion_plots(n):
    #dedicir distribucion en funcion del numero de datos a representar
    if n <=4: #una sola columna
        i=int(n/1)
        sub_posicion=str(i)+'1'
        
    elif n <=8: #dos columnas de hasta 3 elementos
        i=int(n/2) + n%2
        sub_posicion=str(i)+'2'

    else: #tres columnas de n elementos
        i=int(n/3) + n%3
        sub_posicion=str(i)+'3'

    lista_posiciones = []
    for posicion in range(1,n+1):
        di = sub_posicion + str(posicion)
        distribucion = int(di)
        lista_posiciones.append(distribucion)

    return (lista_posiciones)

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------  

#generar lista de colores para las graficas
def generar_colores(n=10):
    lista_color = []

    if n<=10:
        colores = mcolors.TABLEAU_COLORS
        for name, number in colores.items():
            lista_color.append(name.split(":")[1])

    else:
        colores = mcolors.CSS4_COLORS
        for key in colores:
            lista_color.append(key)
    return lista_color

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------  

def subplot_grafico(apariencia, puntos_eje_x, datos_por_sensor_y, etiqueta, orden_tiquetas, minimos_maximos, soft=False):
    try:
        posicion = apariencia[0]
        color = apariencia[1]
        nombre = apariencia[2]
        ax = fig.add_subplot(posicion)
        ax.grid(True, lw = 0.5, ls = '--', c = '.75')
        
        if soft==True:
            #---- reduccion de ruido a los sensores -------
            datos_originales = datos_por_sensor_y[:]    #por comodidad copiamos la lista con otro nombre
            datos_suavizados = []
            
            if nombre == 'pH' or nombre == 'CO2':       #en el caso de los sensores con mucho ruido
                factor_suavizado = 8                    #numero de muestras sobre las que se hace la media apra suavizar
            else:
                factor_suavizado = 3
            
            for indice in range(len(datos_originales)):
                if (indice > factor_suavizado):
                    dato_suave = 0
                    for x in range (indice-(factor_suavizado+1),indice):
                        dato_suave += datos_originales[x]
                    dato_suave = dato_suave /(factor_suavizado+1)
                else:
                    dato_suave = datos_originales[indice]
                datos_suavizados.append(dato_suave)
            ax.plot(puntos_eje_x[factor_suavizado+1:], datos_suavizados[factor_suavizado+1:], lw = 1.5, c = color)
            #---- fin reduccion de ruido a los sensores -------

        else:
            ax.plot(puntos_eje_x, datos_por_sensor_y, lw = 1.5, c = color)  #sin reduccion de ruido

        margen = (minimos_maximos[1] - minimos_maximos[0])*0.1     
        ax.set_ylim(minimos_maximos[0]-margen, minimos_maximos[1]+margen)
        ax.set_ylabel(nombre) #pone el nombre en el lateral junto a la escala
        #ax.set_title(nombre) #pone el nombre en la parte superior

        ax.set_xticks(orden_tiquetas, minor=False)
        ax.set_xticklabels(etiqueta, size = 'small', color = 'b') 
        
        

    except Exception as e :
        print ("Error Dibujando SUBPLOT")
        print(e)

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------  
 
def dibujar_grafica(datos_brutos_experimento):
    '''
    Funcion para realizar la representacion de la grafica con los datos que se van adquiriendo de ARDUINO
    Esta sera la grafica que visualizamos en la maquina en la que se ejecuta el bot
    y que enviaremos a los clientes cuando nos la soliciten.
    Esta grafica representa siempre las ultimas 24 horas
    Tambien en esta funcion nos encargamos de realiazar los calculos (max, min...).
    recibe una lista que contiene elementos que a su vez son listas/tuplas con todos los datos de interes:

    '''

    try:
        print (epochDate(time.time()), " DEBUG >> dibujando grafica")
        if(len(datos_brutos_experimento) >1440):
            datos_brutos_experimento = datos_brutos_experimento[-1440:]
        # [ [              1               ], [              2               ], ....]   
        # [ [[metadatos1],[datos sensores1]], [[metadatos2],[datos sensores2]], ]
        # [metadatos] = ID, FECHA, RELOJ >> 2019_05_11 19:38:02
        # [datos sensores] = [sensor_A, sensor_B....]  
        
        #horas para las etiquetas de la grafica
        horas = [elemento[0][2][:2]for elemento in datos_brutos_experimento] #recortamos para dejar solo las horas

        #datos de sensores para los ejes Y        
        n_muestras = len(datos_brutos_experimento)

        #creamos una lista de listas (una por cada sensor)
        datos_por_sensor_y = [] #[[lista_sensor1], [lista_sensor2]...], una lista por cada sensor

        #extraemos los datos de los sensores: datos_brutos_experimento[n][1] (dejamos de lado los metadatos)
        datos_sensores = [elemento[1]for elemento in datos_brutos_experimento]
    
        #ahora generamos una lista con los datos de cada sensor de forma individual
        for n in range (len(datos_sensores[-1])):   # mejor coger el ultimo elemento :)
            lista_por_sensor = [elemento[n]for elemento in datos_sensores]
            datos_por_sensor_y.append(lista_por_sensor)

    except Exception as e:
        print ("--------------------------------------")
        print ("ERROR al asignar datos para la grafica")
        print(e)
        return (False)    
    
    try:

        # //---------------------------------------------------------------\\
        #      -- Preparacion de datos para las representaciones graficas--      
        # //---------------------------------------------------------------\\
        

        
        #generacion de lista de valores eje x
        index  = 0
        puntos_eje_x=[]
        while index < n_muestras:
            #creamos una lista que seran los indices de muestra, para poner en el eje x de la grafica
            puntos_eje_x.append(index) #lista para los datos que se representaran en el eje x
            index  += 1 #incrementamos el indice para recorrer las listas
            
        #aprovechamos este punto para obtener el valor min y max de cada sensor
        # que nos sera util para establecer los rangos al dibujar la grafica
        minimos_maximos = []
        lineas_medias = []
        for n in range(len(datos_por_sensor_y)):
            dato_min = (min(datos_por_sensor_y[n]))
            dato_max = (max(datos_por_sensor_y[n]))
            #cada valor añadido sera una lista con dos valores, (el min y el max de cada sensor)
            minimos_maximos.append([dato_min, dato_max])
        
        orden=[]        #lista para almacenar la posicion de las etiquets horarias
        etiqueta=[]     #lista que contendra las etiquetas horarias de la grafica
         
        #SECCION PARA EL ETIQUETADO HORARIO DEL EJE X
        etiquetaEnCurso = -1 #como primera etiqueta ponemos una hora fuera del rango posible 
        muestrasHoraEnCurso = 0
        #recorremos  toda la lista de horas buscando un cambio
        for n in range (0,n_muestras):               # valores de (0 a n_muestras-1)
            if horas[n] != etiquetaEnCurso:          # ante una hora nueva en la lista de horas...
                etiquetaEnCurso = horas[n]           # actualizamos la etiqueta en curso para la comparacion de la busqueda 
                etiqueta.append(etiquetaEnCurso)     # almacenamos la nueva etiqueta que acabamos de localizar  
                orden.append(n)                      # y su posicion
                muestrasHoraEnCurso = n_muestras - n # localizado el ultimo cambio de hora,
                                                     # las muestras que queden son las de la hora en curso
        # Titulo de la ventana
        #plt.title('Captura de datos Experimento BIOCLIMATICO 2019, v1.0')

        fig.canvas.set_window_title('INOPYA')
        #style.use('fivethirtyeight')

        #reducir el numero de etiquetas a la mitad cuadno empiezan a ser muchas
        if len(etiqueta)>12:
            orden = orden[::2]
            etiqueta = etiqueta[::2]

        #añadir los subplots al grafico (posicion, color, nombre_sensor)
        for n in range(len(lista_posicion_plots)): #datos_por_sensor_y
            subplot_grafico([lista_posicion_plots[n], lista_colores_grafica[n],lista_nombres_sensor[n]], \
                            puntos_eje_x, datos_por_sensor_y[n], etiqueta, orden, minimos_maximos[n], soft=True)
      


        label_eje_x = 'MUESTRA:  ' +str(len(lista_Datos_Experimento)) +' (' + str(muestrasHoraEnCurso)+')' + \
        '   FECHA:  ' + reloj.fecha + '     HORA LOCAL:  ' + ('00'+str(HORA))[-2:] + ':' +('00'+str(MINUTO))[-2:]

        plt.xlabel(label_eje_x, horizontalalignment='left') #comun para los dos subplots right

        datos_singulares = minimos_maximos
        
        return datos_singulares
          
    except Exception as e :
        print ("Error Dibujando grafica")
        print(e)
        return(False)


#----------------------------------------------------------------------------------------------------
#  FIN DEL BLOQUE DE DEFINICIÒN DE FUNCIONES
#----------------------------------------------------------------------------------------------------



#mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm

#   INICIO DEL PROGRAMA COMO TAL  (creaccion de instancia a clases y algunas otras definiciones relacionadas con los tiempos)

#mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm



#creacion de un reloj con hora local que habra que actualizar con su metodo update() cuando queramos saber la hora actual
reloj = RelojLOCAL()
reloj.update()

FECHA = reloj.fecha
RELOJ = reloj.reloj
DIA = int(reloj.dia)
HORA = int(reloj.hora)
MINUTO = int(reloj.minuto)
SEGUNDO = int(reloj.segundo)

#Variables para el control de tiempos en al gestiosn de procesos / errores   
nombre_fichero_diario = reloj.fecha2 # ".dat" #nombre del fichero Diario tomado del dia en que se inicia el programa

dia_en_curso = int(reloj.dia)


#====================================================================================================
# PUERTO SERIE PARA COMUNICACION CON ARDUINO
#====================================================================================================
# Crear una instancia de Serial para 'dialogar' con Arduino
'''
En este bloque creamos una instancia al puerto donde se conecta arduino y verificamos su validez.
Tambien se encarga de vigilar eventuales fallos de conexion y evitar los bloqueos del programa,
encargandose de gestionar la reconexion de arduino incluso aunque esta se haga en un puerto distinto
del que se conecto inicialmente
'''

puertoDetectado = detectarPuertoArduino() #detactamos automaticamente el puerto

if (puertoDetectado != ''):
    arduinoSerialPort = serial.Serial(puertoDetectado, VELOCIDAD_PUERTO_SERIE) #usamos el puerto detectado
    print ("\n ** ARDUINO CONECTADO EN " + puertoDetectado + " ** \n")

else:
    print (" == ARDUINO NO PRESENTE == ")
    print ("    conecte la estacion antes de 60 segundos\n")

    tiempoInicio = time.time()
    ActualTime = time.time()
    while (ActualTime - tiempoInicio < 60): 
        puertoDetectado = detectarPuertoArduino() #detactamos automaticamente el puerto
        ActualTime = time.time()
        if (puertoDetectado != ''):
            arduinoSerialPort = serial.Serial(puertoDetectado, VELOCIDAD_PUERTO_SERIE) #usamos el puerto detectado
            print ("\n ** ARDUINO CONECTADO EN " + puertoDetectado + " ** ")
            break

if (puertoDetectado == ''):
    print ("\n == CONECTE LA ESTACION Y REINICIE EL PROGRAMA == \n")





# mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
# =========================================================================================================
#   BUCLE PRINCIPAL  DEL PROGRAMA   (SISTEMA VEGETATIVO)
# =========================================================================================================
# mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm



# Bucle para realizar las mediciones, calculos asociados a ellas y representacion de las mismas en forma grafica
'''
#Si hay AUTOMATA CONECTADO creamos la grafica y resto de procesos
asociados a la adquisicion de datos y su representacion, si no, salimos

Entramos aqui solo si se ha detectado una placa arduino o compatible para la adquisicion de datos

'''

if puertoDetectado:  
    # Se prepara la zona de trabajo de la grafica 
    fig = plt.figure()
    fig.set_size_inches(10, 6)  #asignamos un tmño 'generoso' al grafico apra que se vea con claridad
    #hacemos una consulta a la estacion para despertarla (por si acaso)
    try:
        consultar_Arduino(0.5)
    except:
        pass

    # **** ENVIO DE MENSAJE PARA NOTIFICAR AL ADMINISTRADOR DE UN REINICIO DEL SISTEMA  ****
    if FLAG_estacion_online == True and ADMIN_USER != None: 
        try:
            send_message ('Estacion Reiniciada\n'+NOMBRE_SCRIPT_EN_EJECUCION, ADMIN_USER)
        except:
            pass
     
    ''' Cargar datos desde backup si los hubiese para continuar un experimento en curso '''
    
    try:   
        #carga de la lista que continene los datos acumuados
        
        file_datos_experimento = RUTA_PROGRAMA + RUTA_BACKUP + FICHERO_DATOS_EXPERIMENTO
        estado_carga, lista_Datos_Experimento = cargar_datos_desde_fichero(file_datos_experimento)
        if estado_carga == False:
            lista_Datos_Experimento = []
            print ("lista_Datos_Experimento[]  no pudo ser restaurada")
            print ("buscando copia de seguridad...")
            longitud_extension = len(file_datos_experimento.split(".")[-1])
            nombre_con_ruta_backup = file_datos_experimento[:-longitud_extension] + "bak"
            estado_carga, lista_Datos_Experimento = cargar_datos_desde_fichero(nombre_con_ruta_backup)                                                                            
            if(estado_carga==False):
                print ("ERROR CARGANDO DATOS, se reinicia la toma de datos desde cero")
                
        if(estado_carga==True):
            pass
            ultima_valida = lista_Datos_Experimento[-1]
            ultima_valida = ultima_valida[0]
            print("FECHA/HORA Ultima muestra valida: ",ultima_valida[1],ultima_valida[2])

    except:
        lista_Datos_Experimento = []
        print ("ERROR CARGANDO DATOS, se reinicia la toma de datos desde cero") 

    try:   
        #carga de la lista que continene los datos del dia en curso (grafica ultims 24 horas)
        
        file_datos_experimento = RUTA_PROGRAMA + RUTA_BACKUP + FICHERO_DATOS_DIA_EN_CURSO
        estado_carga, lista_Datos_SOLO_dia_en_curso = cargar_datos_desde_fichero(file_datos_experimento)
        if estado_carga == False:
            lista_Datos_SOLO_dia_en_curso = []
            print ("lista_Datos_SOLO_dia_en_curso[]  no pudo ser restaurada")
            print ("buscando copia de seguridad...")
            longitud_extension = len(file_datos_experimento.split(".")[-1])
            nombre_con_ruta_backup = file_datos_experimento[:-longitud_extension] + "bak"
            estado_carga, lista_Datos_SOLO_dia_en_curso = cargar_datos_desde_fichero(nombre_con_ruta_backup)                                                                            
            if(estado_carga==False):
                print ("ERROR CARGANDO DATOS DIA EN CURSO, El dia comienza ahora :(")
                
        if(estado_carga==True):
            pass
            print("CARGA DE DIA EN CURSO CORRECTA")

    except:
        lista_Datos_SOLO_dia_en_curso = []
        print ("ERROR CARGANDO DATOS DIA EN CURSO, El dia comienza ahora :(") 
                       
                                                                                        
            
    print ("FECHA y HORA DEL REINICO DEL PROGRAMA:   ", reloj.fechayhora)
    print ("\n\n")



    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
    #  INICIO DE LA ADQUISICION Y REPRESENTACION      
    # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm

    #etiquetas de los graficos de cada sensor
    numero_sensores = 6
    lista_nombres_sensor = ['Temp_int', 'Humedad_int', 'pH', 'CO2', 'Presion', 'Temp_ext'] #nombres sensores (en orden)

    #generar colores y posicion de los graficos de forma automatica
    lista_colores_grafica = generar_colores(numero_sensores) #numero de colores a generar. Igual al numero de sensores
    lista_posicion_plots = generar_posicion_plots(numero_sensores)

    #generar colores y posicion de los graficos de forma MANUAL (usar con cautela)
    '''
    Descomentar esta seccion si deseas controlar el aspecto de forma manual
    Consulta la ayuda de MATPLOTLIB para saber mas acerca de los graficos
    '''
    ##lista_posicion_plots = [323,321,322,324,326,325]                            #descomentar para orden personalizado
    ##lista_colores_grafica = ['red','green','blue','black','purple','orange']    #descomentar para colores personalizados


    while (FLAG_run == True):
        reloj.update()
        FECHA = reloj.fecha
        RELOJ = reloj.reloj
        DIA = int(reloj.dia)
        HORA = int(reloj.hora)
        MINUTO = int(reloj.minuto)
        SEGUNDO = int(reloj.segundo)

                    
        # ========== ADQUISICION de datos desde ARDUINO ================================================================
        try:
            if time.time() >= minuto_adquisicion_datos + TIEMPO_ENTRE_MUESTRAS:
                muestra_nuevo_formato = []
                #print (epochDate(time.time()), "DEBUG >> peticion")
                muestra_datos = consultar_Arduino(.5)
                while muestra_datos == None:
                    #print (epochDate(time.time()), " DEBUG >> muestra de datos NONE")
                    muestra_datos = consultar_Arduino(2) #si hubo fallo, damos un poco mas de tiempo en las siguientes peticiones

                if muestra_datos != None and str(type(muestra_datos)) == "<class 'list'>":
                    print (epochDate(time.time()), " DEBUG >> muestra de datos: ", muestra_datos)

                    ##comprobar que la muestra es correcta  (establecer las condiciones que deseemos, mayores de un valor, menores, en un rango...)
                    if muestra_datos[0] !=None and muestra_datos[1] !=None and muestra_datos[2] !=None:
                        FLAG_reinicio_Arduino = False
                        valor_sensores_Now = muestra_datos[:]
                        ultimos_valores_validos = muestra_datos[:] 
                        
                        # TEMPERATURA_INT
                        # HUMEDAD_INT
                        # PH 
                        # CO2(PPM)
                        # PRESION  valor_sensor_5_Now
                        # TEMPERATURA_EXT                          
                            
                        #si hay muestra valida, Creacion de METADATOS
                        muestra_metadatos = []
                        muestra_metadatos.append(ID_ESTACION_BIO)  # Sustituir con un ID propio de cada estacion para que los datos
                                                            # sean siempre reconocibles aun que se trunque un archivo
                        muestra_metadatos.append(FECHA) # Insertamos los datos de fecha y hora en la lista
                        muestra_metadatos.append(RELOJ)
                        #con los metadatos creamos una lista y con los datos de los sensores otra lista
                        #con estas dos sublistas formamos una lista (muestra completa) que son los 'puntos' que iremos añadiendo
                        #Ahora la muestra es completa: [[metadatos], [Valores actuales]]
                        #Cada punto guardado es una lista donde:
                        #lista[0], son los metadatos
                        #lista[1], son los datos de los sensores
                        # De esta forma no hay problema si se añaden mas metadados o mas datos en el futuro.

                        muestra_nuevo_formato.append(muestra_metadatos)
                        muestra_nuevo_formato.append(muestra_datos)

                        #Ahora la muestra es completa: [[metadatos], [Valores actuales]]

                        lista_Datos_Experimento.append(muestra_nuevo_formato)
                        lista_Datos_SOLO_dia_en_curso.append(muestra_nuevo_formato)

                        #si todas las tareas se realizan correctamente, se actualiza el minuto para la proxima toma de muestras
                        #en caso contrario  en el proximo ciclo del programa se volvera a intentar otra toma de datos
                        minuto_adquisicion_datos = time.time()

                #Si se produce algun error en la adquisicion de datos, dejamos vigentes los ultimos que fueron validos
                #que NO se aplicaran a las listas, PERO sirven para no generar errores en las peticiones
                #de los usuarios que se produzcan mientras se obtienen datos correctos
                else:
                    if FLAG_reinicio_Arduino == False: #esta bandera es para evitar que se traten de conservar
                                                       #valores que no existen (en caso de reinicio)
                        valor_sensores_Now = ultimos_valores_validos[:] 
        except:
            if MINUTO != minuto_error_arduino:       #solo si ha pasado un minuto del ultimo error se notifica
                minuto_error_arduino = MINUTO        #refresco la referencia con el minuto actual
                print (epochDate(time.time()),"ERROR en las lecturas de arduino")

 

        # ========== PREPARAR las listas de DATOS y REPRESENTARLOS EN LA GRAFICA =======================================
        try:
            if len(lista_Datos_Experimento) > 1:
                #if time.time() > minuto_dibujar_grafica + TIEMPO_ENTRE_MUESTRAS: #tiempo entre actualizaciones flexible (se ajusta al tiempo de muestreo)
                if MINUTO != minuto_dibujar_grafica:       #solo actualizamos la grafica cada minuto
                    plt.clf() # esto limpia la información del  área donde se pintan los graficos.

                    #podemos aprovechar la funcion de dibujado para extraer los datos de interes como max, min, medias...
                    #que por ahora no usamos para nada, pero ahí queda
                    datos_de_interes = dibujar_grafica(lista_Datos_Experimento)
                    
                    plt.pause(.025) # Pausa para el refresco del grafico. Es necesaria, si no, no se ve la representacion :(

                    minuto_dibujar_grafica = MINUTO        #solo actualizamos la grafica cada minuto
                    #minuto_dibujar_grafica = time.time()  #tiempo entre actualizaciones flexible
            
        except:
            print (epochDate(time.time()),"ERROR al dibujar grafica")
            time.sleep(25) # pausa de 25 segundos para no llenar la pantalla de mensajes de error

                
        # ========== COPIA de SEGURIDAD de datos automaticamente cada cierto tiempo (INTERVALO_BACKUP) ==================
        try:      
            if  FLAG_backup_datos_Enabled == True and FLAG_momento_salvado_datos == True and MINUTO % INTERVALO_BACKUP == 0 and SEGUNDO < 20:
                ruta = RUTA_PROGRAMA + RUTA_BACKUP
                nombreCompletoDat = ruta + FICHERO_DATOS_EXPERIMENTO
                
                print (epochDate(time.time())," Realizando copias de seguridad...")                
                salvar_Backup_datos(lista_Datos_Experimento, nombreCompletoDat)
                print("\t\t\tOK AUTO_BACKUP DATOS COMPLETOS")

                nombreCompletoDat = ruta + FICHERO_DATOS_DIA_EN_CURSO
                salvar_Backup_datos(lista_Datos_SOLO_dia_en_curso, nombreCompletoDat)
                print("\t\t\tOK AUTO_BACKUP SOLO DIA EN CURSO")
                
                
                #convertir a TXT y salvar
                nombreCompletoTxt = ruta + FICHERO_TXT_EXPERIMENTO
                convertir_Datos_to_TXT(lista_Datos_Experimento, nombreCompletoTxt, cabecera=cabeceraTXTdatos)
                print("\t\t\tOK AUTO_BACKUP DATOS COMPLETOS en formato TXT")

                #guardar una copia de la representacion grafica
                nombreCompletoGrafica =  ruta + "experimento_bio.png"
                plt.savefig(nombreCompletoGrafica)
                print("\t\t\tOK AUTO_BACKUP datos graficos")
                # si la bandera se iguala a FALSE en este punto, garantizamos que todo ha salido bien
                FLAG_momento_salvado_datos = False
                
            if SEGUNDO >= 20:
                #reactivamos la bandera que permite guardar datos si el resto de condiciones son validas
                FLAG_momento_salvado_datos = True
                
        except:
            print ("---------------------------")
            print ("ERROR BACKUP_DATOS")

        # ========== ATENDER TELEGRAMAS ================================================================================ 
        if FLAG_estacion_online == True:
            try:
                #Recibir nuevos mensajes desde TELEGRAM
                atenderTelegramas(telegram_bot_experimento_bio)
            except:
                print ("\nERROR accediendo a telegram\n")

            # ========== GESTIONAR PETICIONES  DE GRAFICA ==================================================================
            try:
                #por si alguien nos pide la grafica          
                if FLAG_enviar_PNG == True:
                    plt.savefig(RUTA_PROGRAMA + RUTA_BACKUP + FICHERO_GRAFICA_EXPERIMENTO)  
                       
                    url = URL+"sendPhoto";
                    files = {'photo': open(RUTA_PROGRAMA + RUTA_BACKUP + FICHERO_GRAFICA_EXPERIMENTO, 'rb')}
                    data = {'chat_id' : chat_id}
                    r= requests.post(url, files=files, data=data)
                    FLAG_enviar_PNG = False
            except:
                print ("ERROR al generar PNG para el cliente")
                
            # ========== GESTIONAR PETICIONES  DE TXT ==================================================================
            try:
                #por si alguien nos pide la informacion en txt          
                if FLAG_enviar_TXT == True:                      
                    url = URL+"sendDocument";
                    files = {'document': open(RUTA_PROGRAMA + RUTA_BACKUP + FICHERO_TXT_EXPERIMENTO, 'rb')}
                    data = {'chat_id' : chat_id}
                    r= requests.post(url, files=files, data=data)
                    FLAG_enviar_TXT = False
            except:
                print ("ERROR al enviar de datos en TXT al cliente") 

            # ========== GESTIONAR PETICIONES  DE BORRADO DE DATOS ==================================================================
            try:
                #por si alguien nos pide borrar datos iniciales (antiguos)    
                if FLAG_delete_old == True:
                    if len(lista_Datos_Experimento) > 17:
                            lista_Datos_Experimento = lista_Datos_Experimento[15:]
                    else:
                        send_message ('datos insuficuentes, intentalo mas tarde', chat_id)
                    FLAG_delete_old = False
            except:
                print ("ERROR al borrar las 15 primeras muestras")
                
            try:
                #por si alguien nos pide borrar datos finales (recientes)        
                if FLAG_delete_new == True:
                    if len(lista_Datos_Experimento) > 17:
                            lista_Datos_Experimento = lista_Datos_Experimento[:-15]
                    else:
                        send_message ('datos insuficuentes, intentalo mas tarde', chat_id)
                    FLAG_delete_new = False
            except:
                print ("ERROR al borrar las 15 ultimas muestras")                


        #GESTION Y TAREAS asociadas al cambio de dia (salvar diario y enviar datos por email a suscriptores)
        
        if DIA != dia_en_curso:
            
            #----------- Guardar de datos de resumen diario --------------------------------------------------------------
            try: 
                FLAG_pruebas = False
                dia_en_curso = DIA      #anulando la condicion al principio evitamos pasar de nuevo si se produce un error en este tramo
                                        #tiene sus ventajas ya que no corrrompe los ficheros si es que llegan a guardarse, pero no
                                        #se reintenta si no se completa y puede quedar alguna tarea pendiente, sea convertir, enviar email...
                
                #crear un nuevo registro con el nombre de: año_mes_dia.*
                ruta = RUTA_PROGRAMA + RUTA_BACKUP + "diarios/"
                #el nombre del fichero corresponde al dia transcurrido, por eso lo generamos en el bloque siguiente
                nombreCompleto = ruta + nombre_fichero_diario

                #salvar registros diarios en formato python pickle             
                salvar_Backup_datos(lista_Datos_SOLO_dia_en_curso, nombreCompleto + ".data")   #Salva los datos diarios a formato *.data

                #salvar registros diarios en formato TXT
                convertir_Datos_to_TXT(lista_Datos_SOLO_dia_en_curso, nombreCompleto + ".txt", cabecera=cabeceraTXTdatos) #convierte y salva los datos diarios a un fichero *.txt
               
                #salvar registros acumulados en formato TXT               
                convertir_Datos_to_TXT(lista_Datos_Experimento, nombreCompleto + "_full.txt")   #Salva los datos acumulados a formato *.txt

                # CAMBALACHE PARA QUE EN LA GRAFICA DE RESUMEN DIARIO APAREZCAN LAS 23:59
                # establecemos nuestras variables horarias manualmente
                HORA = 23
                MINUTO = 59
                #forzamos un redibujado de la grafica con la hora manual establecida
                dibujar_grafica(lista_Datos_Experimento) # llamada sin asignar el retorno a nada, solo nos interesa redibujarla
                # devolvemos la hora real en al seccion de reset (porque aun quedan unos cuantos guardados de grafica)

                #guardar la grafica del dia que acaba de completarse
                plt.savefig(nombreCompleto +".png") 

                if (FLAG_estacion_online == True):
                    try:
                        send_message ("OK GUARDANDO RESUMENES DIARIOS \n" + nombreCompleto, ADMIN_USER)
                    except:
                        pass
                
            except Exception as e:
                print ("---------------------------")
                print (epochDate(time.time()), e)
                print (epochDate(time.time()),"ERROR TEMPORIZADORES NUEVO DIA >> GUARDANDO RESUMEN DIARIO")
                
                if (FLAG_avisar_administrador == True and FLAG_estacion_online == True):
                    send_message ("ERROR TEMPORIZADORES NUEVO DIA >> GUARDANDO RESUMEN DIARIO", ADMIN_USER)
                  
            #----------- SECCION PARA ENVIO DE EMAIL DE RESUMEN DIARIO ----------------------------------
            try:
                nombreRutaConExtension = RUTA_PROGRAMA + RUTA_BACKUP + FICHERO_TXT_EXPERIMENTO
                status1 = convertir_Datos_to_TXT(lista_Datos_SOLO_dia_en_curso, nombreRutaConExtension, \
                                                 cabecera=cabeceraTXTdatos)
                status2 = enviarEmail(nombreRutaConExtension)
                if(status1==True and status2==True):
                    send_message("EMAIL enviado correctamente", ADMIN_USER)
                else:
                    send_message("ERROR al enviar Email diarios", ADMIN_USER)
                    print ("ERROR al enviar Email diarios")
            except:
                print ("ERROR al enviar Email diarios")
                send_message("ERROR al enviar Email diarios", ADMIN_USER)
               
            #----------- SECCION PARA EL RESET DE LA INFORMACION DIARIA (reset del dia en curso) ----------------------------------
            try:
                #reset de listas de informacion diaria
                lista_Datos_SOLO_dia_en_curso = []

                #actualizamos el nombre con que se ha de guardar el DIARIO (en el nuevo dia, ya que son las 12 de la noche)
                nombre_fichero_diario = reloj.fecha2 #nuevo nombre (una vez que han dado las doce de la noche) y se ha terminado de guardar cosas
                print ("---------------------------")
                print (epochDate(time.time()),"OK SALVADO DIARIO\n")

                # devolvemos a nuestras variables la hora real
                HORA = int(reloj.hora)
                MINUTO = int(reloj.minuto)
                
            except Exception as e:
                print ("---------------------------")
                print (epochDate(time.time()), e)
                print (epochDate(time.time()),"ERROR TEMPORIZADORES NUEVO DIA >> RESET VARIABLES DIARIAS")
                
                if (FLAG_avisar_administrador == True and FLAG_estacion_online == True):
                    send_message ("ERROR TEMPORIZADORES NUEVO DIA >> RESET VARIABLES DIARIAS", ADMIN_USER)


        plt.pause(.025)  ## refresco continuo del area de la grafica.
    plt.close('all') 


if puertoDetectado:                               
    print ("\n\> PROGRAMA TERMINADO - FIN DE ADQUISICION DE DATOS\n")

else:
    print ("     << ERROR >> MICROCONTROLADOR NO PRESENTE\n")

   


