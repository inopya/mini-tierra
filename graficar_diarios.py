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
# *     Graficar diarios  v1.0   Fecha: 11/11/2019     * #
# ****************************************************** #
##########################################################

'''
    Utilidad que nos permite generar graficos PNG
    desde los ficheros de datos diarios.
'''


#--------------------------------------------------------
# IMPORTACION DE MODULOS
#--------------------------------------------------------


# FILTRADO DE ERRORES
#matplotlib (al menos la version que uso) me genera algunos mensajes de advertencia que prefiero no ver
import warnings
warnings.filterwarnings("ignore")

# TIEMPOS, FECHAS
from time import sleep      #pausas...
import datetime


#INTERACTUAR CON EL SISTEMA OPERATIVO
    
import sys              #Conocer el tipo de sistema operativo
import time             #manejo de funciones de tiempo (fechas, horas, pausas...)
import os               #manejo de funciones del sistema operativo 
from os import walk     #funciones para movernos por directorios
import glob



# REPRESENTACION GRAFICA DE DATOS
import matplotlib                               #funcionalidad para representacion grafica de datos
import matplotlib.pyplot as plt                 #por comodidad al llamar esta funcionalidad
from matplotlib.ticker import MultipleLocator   #para crear leyendas en los graficos
from matplotlib import style

import matplotlib.colors as mcolors             #para manejar los colores de matplotlib

# FUNCIONES MATEMATICAS AVANZADAS
import numpy as np
import math


#====================================================================================================
#  INICIO DEL BLOQUE DEFINICION DE CONSTANTES Y VARIABLES GLOBALES PARA EL PROGRAMA 
#====================================================================================================


#Ruta absoluta en la que se encuentra el script. Util apra las llamadas desde el inicio del sistema
RUTA_PROGRAMA = os.path.dirname(os.path.abspath(__file__)) +'/'
NOMBRE_SCRIPT_EN_EJECUCION = os.path.basename(__file__)
RUTA_BACKUP = ""#'backup/' 



print ("==================================================")
print ("\nRuta ABSOUTA DEL PROGRAMA:\n", RUTA_PROGRAMA)
print ("\nNombre del fichero en ejecucion:\n", NOMBRE_SCRIPT_EN_EJECUCION)
print ("\n==================================================\n\n")

#----------------------------------------------------------------------------------------------------
#  FIN DEL BLOQUE DEFINICION DE VARIABLES GLOBALES
#----------------------------------------------------------------------------------------------------



#====================================================================================================
#  INICIO DEL BLOQUE DEFINICION DE FUNCIONES 
#====================================================================================================

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

#localizar los ficheros de datos de cada dia
def localizar_diarios_datos():
    txt_files = glob.glob(RUTA_PROGRAMA+"*.txt")
    lista_dias = []
    for nombre in txt_files:
        candidato = (nombre.split("\\")[-1])
        if candidato[:4] == "2019":
            lista_dias.append(nombre.split("\\")[-1])  
    #print ("DEBUG >>   ",len(lista_dias), lista_dias)
    return lista_dias

#-----------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------  

def cargar_diario_de_datos(fichero_diario):
    #Cardade datos correspondientes a un dia para su representacion
    FLAG_cabecera = False

    file_in = open(fichero_diario, 'r') 
    lineas = file_in.readlines()

    if (FLAG_cabecera == True):
        cabecera = lineas[0]
        indice_inicial = 1
    else:
        indice_inicial = 0

    hora = ""  #hora ide la ultima muestra, la mostramos en el grafico

    #esta lista es muy importante ya que guardaran los datos de las muestras para dibujar de la grafica
    lista_datos_experimento = []


    for n in range(indice_inicial, len(lineas)):
        linea_actual = lineas[n]
        lista_actual = linea_actual.split("\t")
        lista_actual = lista_actual[1:-1]
        metadatos = lista_actual[:3]
        datos = lista_actual[3:]
        datos_numericos=[]
        for dato_string in datos:
            datos_numericos.append(float(dato_string))
        muestra = []
        muestra.append(metadatos)
        muestra.append(datos_numericos)
        lista_datos_experimento.append(muestra)
        hora = lista_actual[2][:-3]

    return hora, lista_datos_experimento

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

# REPRESENTACION GRAFICA

def subplot_grafico( apariencia, puntos_eje_x, datos_por_sensor_y, etiqueta, orden_tiquetas, minimos_maximos, soft=False):
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
        # [metadatos] = ID, FECHA, RELOJ >> ID_ESTACION 2019_05_11 19:38:02
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

        #reducir el numero de etiquetas a la mitad cuando empiezan a ser muchas
        if len(etiqueta)>12:
            orden = orden[::2]
            etiqueta = etiqueta[::2]

        #añadir los subplots al grafico (posicion, color, nombre_sensor)
        for n in range(len(lista_posicion_plots)): #datos_por_sensor_y
            subplot_grafico([lista_posicion_plots[n], lista_colores_grafica[n],lista_nombres_sensor[n]], \
                            puntos_eje_x, datos_por_sensor_y[n], etiqueta, orden, minimos_maximos[n], soft=True)
        


        label_eje_x = 'MUESTRAS:  ' +str(len(lista_Datos_Experimento)) + \
        '   FECHA:  ' + FICHERO_TXT_EXPERIMENTO[:-4] + '     HORA LOCAL:  ' + HORA

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





# mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
# =========================================================================================================
#   BUCLE PRINCIPAL  DEL PROGRAMA  
# =========================================================================================================
# mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm

numero_sensores = 6
lista_nombres_sensor = ['Temp_int', 'Humedad_int', 'pH', 'CO2', 'Presion', 'Temp_ext'] #nombres sensores (en orden)

#generar colores y posicion de los graficos de forma automatica
lista_colores_grafica = generar_colores(numero_sensores) #numero de colores a generar. Igual al numero de sensores
lista_posicion_plots = generar_posicion_plots(numero_sensores)

#generar colores y posicion de los graficos de forma MANUAL (usar con cautela)
##lista_posicion_plots = [323,321,322,324,326,325]                            #descomentar para orden personalizado
##lista_colores_grafica = ['red','green','blue','black','purple','orange']    #descomentar para colores personalizados

#localizar y cargar los ficheros diarios del experimento
lista_ficheros_datos = localizar_diarios_datos()

for FICHERO_TXT_EXPERIMENTO in lista_ficheros_datos:
    FICHERO_GRAFICA_EXPERIMENTO = FICHERO_TXT_EXPERIMENTO[:-4]+".png"
    lista_Datos_Experimento = []
    HORA, lista_Datos_Experimento = cargar_diario_de_datos(FICHERO_TXT_EXPERIMENTO)
 

    # ========== REPRESENTAR LA GRAFICA Y GENERAR UNA COPIA EN PNG =======================================
    try:
        if len(lista_Datos_Experimento) > 1:
            fig = plt.figure()
            fig.set_size_inches(14, 8)  #asignamos un tamaño 'generoso' al grafico apra que se vea con claridad
            plt.clf() # esto limpia la información del  área donde se pintan los graficos.

            dibujar_grafica(lista_Datos_Experimento)
                
            plt.pause(.025) # Pausa para el refresco del grafico. Es necesaria, si no, no se ve la representacion :(
    except:
        print (epochDate(time.time()),"ERROR al dibujar grafica")
                    
    try:
        plt.savefig(RUTA_PROGRAMA + RUTA_BACKUP + FICHERO_GRAFICA_EXPERIMENTO)
        #time.sleep(1) #pausa entre generacion de graficas, por puro gusto de perder el rato
        plt.close('all') 
    except:
        print ("ERROR al generar PNG para el cliente")
                    


