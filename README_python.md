# EXPLICACION DE LOS FICHEROS PYTHON

**===================================================**
## capturar_datos_experimento.py
**===================================================**

	Es el programa central. Se encarga de comunicar con Arduino, recopilar los datos, 
	registrarlos en un fichero y generar graficas con ellos en 'tiempo real' 
	(la grafica se actualiza cada minuto, salvo que se indique lo contrario).

### Puerto serie

	La velocidad del puerto serie esta establecida por defecto en 115200.
	Programar dicha velocidad en el puerto serie de Arduino o cambiar la de python.
	En cualquier caso, debemos asegurarnos que sean la misma.
	En cuanto al puerto con el que el programa se comunica, no hay nada que configurar,
	Python buscará automaticamente un dispositivo conectado, tanto el Linux como en Windows.
	Ojo, si hay mas de de un dispositivo conectado en los puertos serie podemos 'tener problemas'
	y no detectar correctamente a nuesto Arduino.

### Modo online y modo offline

	Disponemos de deos modos de funcionamiento: *online* y *offline*
	El registro de datos y la representacion graficas estan habilitados siempre,
	pero el modo online permite:
	- que se interactue con el mediante un bot de telegram: 
		- para recibir informacion instantanea de los datos monitorizados.
		- recibir via telegram un fichero con todos los datos acumulados hasta ese momento
		- recibir graficas del momento actual (muestran ultimas 24 horas de toma de datos)
		- forzar el envio de la informacion recopilada al correo o correos prefijados
		- borrar algunas de las muestras tomadas al inio o fin de la serie (puede ser de utilidad) 
		  si se produce alguna manipulacion del sistema monitorizado 
		  y no se desea guardar esa 'perturbacion'
		  
	- el envio de informacion a un email periodicamente al cierre de cada dia.


### Telegram (modo online)

    *Para crear tu bot telegram añade a tus contactos a BotFather y sigue sus instrucciones*
	Obten el token de tu bot y asignala a la variable **TOKEN**.
	
	Es muy recomendable configurar la variable **ADMIN_USER** con tu chadId de usuario 
	Si no lo conoces (en tu movil andrid puedes localizarlo, o bien puede poner en marcha el programa 
	con el bot configurado y enviarle un mensaje cualquiera. 
	En la consola de python veras aparecer una inea de texto
	con el formato: fecha, hora, CHAD_ID, nombre, mensaje	
			ejemplo: **2019-11-13 14:48:58 >>> 145678: NombreUsuario --> texto_mensaje**,
	ya que si lo dejamos esta en su valor por defecto 'None' cualquiera que se conecte a 
	nuestro bot pueda hacer todas las funciones.
	Una vez configurada, ciertos comandos 'peligrosos' como borrar datos 
	o parar el experimento estaran restringidos para uso exclusivo del administrador/propietario.
	En caso de que un usuario no autorizado los ejecute, recibira en respuesta un escueto "ok", 
	pero no se realizará ninguna accion por parte del programa.

### Email (modo online)

	Asi mismo para poder usar las funciones de correo deben configurarse las variables
	SMTP_CORREO_ENVIOS   (servidor smtp del usuario)
	EMAIL_CORREO_ENVIOS = (direccion de correo desde la que se enviaran los mensajes)
	PASS_CORREO_ENVIOS =  (contraseña de la direccion de correo de envio)
	REMITENTE_CORREO_ENVIOS = (direccion de correo desde la que se enviaran los mensajes),
	si usais una direccion de gmail en esta variable podeis poner el texto que deseeis

	Asi mismo en la variable *'lista_correo_experimento'* debe contener una o mas direcciones de destino
	lista_correo_experimento = ['sorbasdigital@hotmail.com','direccion2','direccion3']  

### Lista de comando telegram

	- /start - inicia el bot
	- /ayuda - Mostrar esta Ayuda
	- /email - envia datos completos por email
	- /info - Mostrar datos actuales
	- /txt - envia datos completos a telegram
	- /fig - Grafico de Evolucion
	- /deleteOld - Borra los 15 primeros datos
	- /deleteNew - Borra los 15 ultimos datos
	- /stop - Finaliza el experimento
	- /save - Realiza una copia de seguridad




### Suavizado de gráica

	Dado que algunos sensores (especialmeten los analogicos: LDRs, sensores de gas, de pH...) 
	suelen ser algo ruidosos, en el apartado de funciones para dibujar la grafica, 
	en la llamada a la funcion **subplot_grafico()**, se dispone del parametro **soft** 
	que si se activa genera graficos suavizados eliminando en la medida de lo posible 
	el 'ruido' de los sensores.
	Recordad que aunque se active la reduccion de ruido, 
	esta no afecta a los datos que se recopilan. 
	El suavizado gráfico afecta solo a la representación.


### Registro/Salvado de datos:

* El programa realiza copias de los datos cada cierto tiempo, 
  programable mediante la variable **INTERVALO_BACKUP**
  Estas copias se colocaran en la carpeta de trabajo '/backup'
	
* Asi mismo, al terminar el dia en curso:
	- realiza una copia de los datos del dia en curso (en formato python pickle) con el nombre 'año_mes_dia'.data 
	- realiza una copia de los datos del dia en curso con el nombre 'año_mes_dia'.txt
	- realiza una copia del acumulado de los datos que se guarda con el nombre 'año_mes_dia_full'.txt
 
	Estas copias se colocaran en el subdirectorio '/diarios' de la carpeta de trabajo '/backup'
	
	

**===================================================**
## * extraer_diarios.py
**===================================================**

	Utilidad Python para trocear por dias el fichero de datos acumulados en formato txt
	A priori no es de gran utilidad ya que el programa realiza copias diarias.
	Lo hice a raiz de un fallo de sistema que me impidio acceder a los datos diarios 
	y la necesidad de reutilizar una copia valida de datos acumulados.
	
	

**===================================================**
## * graficar_diarios.py
**===================================================**

	Permite realizar graficas desde ficheros diarios en formato txt.
	Creada al tiempo de la de extraer diarios para solventar dicha contingencia.
	
