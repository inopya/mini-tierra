# Mini tierra
***Experimento bioclimatico y utilidades***

#### Reproduciendo en casa el experimento bioclimatico presentado en el biotecnoencuentro de Pulpi en octubre de 2019


![](./imagenes/grafica_soft.png)

###### *ejemplo de captura y representacion de datos en funcionamiento*


***UN POCO DE HISTORIA***

Primero de todo, que dicho experimento aun se puede encontrar en el repositorio Biot.

Dado que el programa de adquisision de datos de Biot fue una version bastante reducida de mi estacion meteorológica @meteosorbasbot, en esta reproduccion casera de dicho experimento sobre los gases de efecto invernadero se 
ha usado una version mas parecida a mi programa base de adquisicion y representacion (aunque no completa). No elimino de momento el repositorio original del Biot, pero es conveniente usar los programas de aqui en lugar de aquellos.


***CONTENIDO DE ESTE REPOSITORIO***

* CARPETA> calibracion_MQxx:
 *Utilidad Arduino para la calibracion del MQ135 para CO2*
* CARPETA> calibracion_sonda_PH:
 *Utilidad Arduino para la calibracion de la sonda de Ph*
* CARPETA> generar_datos_para_debug:
 *Utilidad Arduino para generar datos aleatorios. Para pruebas con el programa de adquisicion python.*
* CARPETA> imagenes:
 *Algunas imagenes del montaje y ejemplo de graficos obtenidos durante el experimento.*
* CARPETA> minitierra_v1.0:
 *Fichero Arduino para el experimento como tal*
 
* FICHERO> capturar_datos_experimento.py: 
 *Archivo Python para la adquisicion de datos, registro, representacion y comunicacion telegram*
* FICHERO> extraer_diarios.py: 
 *Utilidad Python paratrocear por dias el fichero de datos generado durante la adquisicion*
* FICHERO> graficar_diarios.py: 
 *Utilidad Python para generar graficas desde los ficheros diarios de datos*
 
* FICHERO> experimento_minitierra_full.txt: 
 *Resultados del mi experimento durante los dias 03/11/2019 al 12/11/2019. Desde el se pueden exrtaer los diarios y graficarlos con     las utilidades python que hay en este repositorio*
 
 
***MODO DE EMPLEO***

  El fichero "capturar_datos_experimento.py" dispone de opciones para comunicacion mediante un bot de telegram y correo electronico.
  Como algunos sensores, especialmente los analogicos, CO2 y Ph meten algo de ruido, se dispone de una opcion en las llamadas a la funcion 'subplot_grafico()' para poder paliar dicho ruido. Si el parametro 'soft' es 'True' se suavida la curva para minimizar el efecto del ruido.
  Se puede ver un ejemplo de dicho suavizado en dos capturas del experimento que encontrarás en la carpeta imagenes.
  La aplicacion de dicho suavizado no afecta a los datos registrados, solo afecta al modo visualizacion.
  
***SENSORES EMPLEADOS***

**MQ-135**  --->  CO2 _(interior del recipiente)_

**GY-21**  --->  HUMEDAD y TEMPERATURA _(interior del recipiente)_

**Sonda PH 0-14**  -->  PH _(interior del recipiente)_

**BMP180**  --->  TEMPERATURA y PRESION ATMOSF. _(exterior del recipiente)_

