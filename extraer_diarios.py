#!/usr/bin/python
# -*- coding: utf-8 -*-


#       _\|/_   A ver..., ¿que tenemos por aqui?
#       (O-O)        
# ---oOO-(_)-OOo---------------------------------
 
 
##########################################################
# ****************************************************** #
# *          LABORATORIO PARA PRINCIPIANTES            * #
# * Utilidad para separar por dias datos recopilados   * #
# *          Autor:  Eulogio López Cayuela             * #
# *            https://github.com/inopya/              * #
# *                                                    * #
# *     Extraer diarios  v1.0    Fecha: 11/11/2019     * #
# ****************************************************** #
##########################################################

'''
    Utilidad que nos permite trocear en ficheros independientes
    los datos recabados desde Arduino para disponer de ellos
    como informacion relativa a cada dia por separado.
'''

#Si existe una cabecera en el fichero original con los datos del experimento
#podemos dedicir si incluirla o no en cada fichero diario (por defecto no la incluimos)
FLAG_cabecera = False  # False = no se copia la cabecera en cada diario generado

#nombre del fichero con los datos totales del experimento (que contendrá mas de un dia de muestras)
file_entrada = open('experimento_minitierra_full.txt', 'r') 
lineas = file_entrada.readlines()
cabecera = lineas[0]

#La primera linea con datos de interes en la tercera [2] del fichero .txt
indice_inicial = 2                                          
linea = lineas[indice_inicial]                              #cargamos la primera linea util,
lista = linea.split("\t")                                   #la converimos en una lista
lista = lista[2:3]                                          #y localizamos la fecha de la primera muestra
dia = lista[0].split("/")[2]                                #para extraer la informacion del dia

#Nombre actualizado para el fichero que hay que guardar
nombre_fichero = lista[0].replace("/","_")                  #usamos la fecha sustituyendo caracteres no validos

fichero_salida = open(nombre_fichero+".txt", 'w')
if (FLAG_cabecera == True):
    fichero_salida.write(cabecera)

print("DEBUG 1:", "fecha ", lista)
#print("DEBUG 2", "nombre_fichero ", nombre_fichero)


#iniciamos el bucle para detectar los dias dentro del fichero de muestras
#y separarlos en ficheros independientes
print("\n>>> GENERANDO FICHEROS DE DATOS DIARIOS...\n\n")
 
for n in range(indice_inicial, len(lineas)):
    linea_actual = lineas[n]                                #leemos una linea del fichero general de datos
    lista_actual = linea_actual.split("\t")                 #creamos una lista separando por los tabuladores
    lista_actual = lista_actual[2:3]                        #reducimos la lista solo a los elementos de interes (la fecha)
    dia_actual = lista_actual[0].split("/")[2]              #extraemos la informacion del dia
    if(dia_actual != dia):
        fichero_salida.close()                              #cerramos el fichero diario terminado al cambiar de dia
        print("\tGenerado fichero dia ",lista_actual[0])    #DEBUG, mensaje de aviso de fichero generado
        dia=dia_actual                                      #ante un nuevo dia, actualizamos el valor del dia
        nombre_fichero = lista_actual[0].replace("/","_")   #usamos la nueva fecha sustituyendo caracteres no validos
        fichero_salida = open(nombre_fichero+".txt", 'w')   #abrimos un nuevo fichero apra un nuevo dia
        if (FLAG_cabecera == True):
            fichero_salida.write(cabecera)
        fichero_salida.write(linea_actual)                  #Escribimos la primera linea en el nuevo fichero diario    
    else:
        fichero_salida.write(linea_actual)                  #si no hay cambio de dia, añadimos la linea al fichero diario en curso

fichero_salida.close()                                      #cerramos el ultimo fichero diario usado

print("\n\n>>> CREACION DE DIARIOS TERMINADA\n")
