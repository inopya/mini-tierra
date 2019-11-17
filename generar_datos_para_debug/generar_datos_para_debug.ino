/*
#       _\|/_   A ver..., ¿que tenemos por aqui?
#       (O-O)        
# ---oOO-(_)-OOo---------------------------------
 
 
##########################################################
# ****************************************************** #
# *          LABORATORIO PARA PRINCIPIANTES            * #
# *   Generador de datos aleatorios para graficos      * #
# *          Autor:  Eulogio López Cayuela             * #
# *                                                    * #
# *      Generador v1.0     Fecha: 03/11/2019          * #
# ****************************************************** #
##########################################################
*/


#define __VERSION__ "generador de datos aleatorios v1.0\n"


/*
      ===== NOTAS DE LA VERSION "ZANGANO" ===== 
   
 - entrega de datos aleatorios al puerto serie para pruebas con sistemas graficos


    Tamaño actual compilado 2434 bytes de ROM y 192 bytes de RAM

*/




/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
//        IMPORTACION DE LIBRERIAS 
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

// nada en esta seccion             // biblioteca para el sensor de presion y temperatura


/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
//        CREACCION DE OBJETOS
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

// nada en esta seccion


/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
//        SECCION DE DECLARACION DE CONSTANTES  Y  VARIABLES GLOBALES
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

//------------------------------------------------------------------------
// Algunas definiciones personales para mi comodidad al escribir codigo
//------------------------------------------------------------------------
#define AND &&
#define OR ||
#define NOT !
#define ANDbit &
#define ORbit |
#define NOTbit ~
#define XORbit ^


//------------------------------------------------------
//Otras definiciones para pines y variables
//------------------------------------------------------
#define PIN_LED_OnBoard    13   // Led on Board


unsigned long momento_para_adquirir_datos = 0;  //para controlar el momento de tomar muestras



/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
   ****************************************************************************************************** 
                                    FUNCION DE CONFIGURACION
   ****************************************************************************************************** 
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

void setup()
{
  Serial.begin(115200);               //#9600, 19200, 38400, 57600, 115200
  Serial.println (F(__VERSION__));    // mostramos la version por consola, DEBUG

  
  pinMode(PIN_LED_OnBoard, OUTPUT);   // PIN_LED_OnBoard como salida
  digitalWrite(PIN_LED_OnBoard, LOW); // apagamos el led 'On Board'

}



/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
   ****************************************************************************************************** 
                                  BUCLE PRINCIPAL DEL PROGRAMA
   ****************************************************************************************************** 
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

void loop()
{ 
  /* mostrar datos aleatios en el puerto serie */
  unsigned long momento_actual = millis();
  if (momento_actual > momento_para_adquirir_datos){
    momento_para_adquirir_datos = momento_actual + 5000;    //refresca los valortes cada 5 segundos
    //mostarDatosEnPython();                                //si deseamos monitorizar solo en puerto serie
  }
  leerPuertoSerie();            //mostraremos los datos solo si hay peticiones por puerto serie
}



/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
   ###################################################################################################### 
        BLOQUE DE FUNCIONES: LECTURAS DE SENSORES, COMUNICACION SERIE, CONTROL LCD...
   ###################################################################################################### 
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/


/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
//    PUERTO SERIE
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

//========================================================
// FUNCION PARA ACCESO Y LECTURA DEL PUERTO SERIE
//========================================================

int leerPuertoSerie()
{
  /*
  Funcion para atender ordenes a través del puerto serie
  Lee los comandos/parametros que envia python al puerto serie:
  
  - Si el comandos es '*' se realiza una muestra unica de datos
  - Si el comandos es 'x' ordena que cancele el proceso de muestreo y envio de datos
  ---- (Ampliable en un futuro para mas cosas
  */

  int lectura = 'x';                        //por defecto pensamos que no se nos pide nada
  if (Serial.available() > 0) {
     // leer byte
    lectura = Serial.read();
    if (lectura == '*' OR lectura == '+'){  // indicador para mandar una muestra unica al puerto serie
      mostarDatosEnPython();
      return 0;                             //ok, peticion de datos
     } 
  }
  return -1;                                //sin peticion por parte del usuario
}


//========================================================
//  ENVIAR DATOS POR PUERTO SERIE A PYTHON
//========================================================

void mostarDatosEnPython()
{ 
  Serial.flush();
  
  /* FORMATEO de datos y ENVIO al puerto SERIE */
  Serial.print(analogRead(A0));
  Serial.print(F("**"));
  Serial.print(analogRead(A1));
  Serial.print(F("**"));
  Serial.print(analogRead(A2));
  Serial.print(F("**"));
  Serial.print(analogRead(A3));
  Serial.print(F("**"));
  Serial.print(analogRead(A4));
  Serial.print(F("**"));
  Serial.println(analogRead(A5)); 
}



//*******************************************************
//                    FIN DE PROGRAMA
//*******************************************************
