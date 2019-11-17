/*
#       _\|/_   A ver..., ¿que tenemos por aqui?
#       (O-O)        
# ---oOO-(_)-OOo---------------------------------
 
 
##########################################################
# ****************************************************** #
# *          LABORATORIO PARA PRINCIPIANTES            * #
# *        Calibracion sensor de Gases  MQ135          * #
# *          Autor:  Eulogio López Cayuela             * #
# *                                                    * #
# *     CalibracionMQxx  v1.0    Fecha: 11/05/2019     * #
# ****************************************************** #
##########################################################
*/


#define __VERSION__ "Calibracion de sensores MQxx v1.0\n"


/*
      ===== NOTAS DE LA VERSION "ZANGANO" ===== 
 - Version generica para calibracion de sensores de gases de la serie MQxx


   >> Fecha: 11/05/2019
 - Calibrado del sensor de gases MQ135 para usarlo con CO2
   Se debe realizar la calibracion en un entorno con concentracion conocida 
   y manteniendolo previamente encendido al menos un par de horas.
   En nuestro caso y a falta de esa rferencia real, lo calibraremos en las horas centrales del dia
   y usaremos el valor de  415ppm como referencia (Es lo que se estima de media en el planeta)
   
   

    * Las constantes a y b se obtienen de la hoja de caracteristicas
    a = 5.5973021420;
    b = -0.365425824;
    Ro=(Rs/a*(ppm)pow(b))
    Rs = Rsensor_media
    Rsensor_media= (Sumatorio(n) Rs )/n   // n muestras durante 5 minutos cada 1 segundos
    Rs = 1024 * (RL/acd)-RL  <<<  RL = 20k(20000)


  CONEXIONES:
 =======================
  ARDUINO UNO      MQ-135
 =======================
  GND               GND
  5V                Vcc
  A0                A0


    Tamaño actual compilado 5132 bytes de ROM y 196 bytes de RAM
    
*/




/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
//        IMPORTACION DE LIBRERIAS 
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

// nada por ahora

/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
//        CREACCION DE OBJETOS
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

//nada por ahora


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
#define PIN_LED_OnBoard    13                   // Led on Board
#define PIN_MQ135          A0                   //pin al que se conecta nuestro sensor MQxx
#define PPM_REFERENCIA    415                   //ppm del ambiente de calibracion
   
unsigned long momento_para_adquirir_datos = 0;  //para controlar el momento de tomar muestras

boolean FLAG_calibracion = true;                //si "FALSE" podemos usar el programa para monitorizar CO2
float a = 5.5973021420;                         //a y b   constantes del sensor para medidas de CO2
float b = -0.365425824;                         //obtenidas de su hoja de caracteristicas
unsigned long Ro = 532003;                      //Ro del sensor que se ha de calcular calibrandolo. 
                                                //Se usa este valor si no se activa la calibracion




/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
   ****************************************************************************************************** 
                                    FUNCION DE CONFIGURACION
   ****************************************************************************************************** 
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

void setup()
{
  Serial.begin(115200);                   //iniciar el puerto serie
  //delay(10000);                         //descomentar con arduino MICRO, o no da tiempo a mostrar los mensajes de setup
  Serial.println (F(__VERSION__));        // mostramos la version por consola, DEBUG
  Serial.print(F("Ro (referencia) = "));
  Serial.println(Ro);                     //mostrar el valor Ro usado como referencia si no hay calibracion
  
  pinMode(PIN_LED_OnBoard, OUTPUT);       // PIN_LED_OnBoard como salida
  digitalWrite(PIN_LED_OnBoard, LOW);     // apagamos el led 'On Board'

  if (FLAG_calibracion == true){          //bandera de control para la calibracion
    Ro = calibrarCO2();
  }
}



/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
   ****************************************************************************************************** 
                                  BUCLE PRINCIPAL DEL PROGRAMA
   ****************************************************************************************************** 
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

void loop()
{ 
  /* Terminada la calibracion, mostrar medidas reales en funcion de dicha calibracion */
  unsigned long momento_actual = millis();
  if (momento_actual > momento_para_adquirir_datos){
    momento_para_adquirir_datos = momento_actual + 5000;    //una muestra cada 5 segundos
    int ppm = medirCO2(PIN_MQ135);
    /* mostrar por puerto SERIE */
    Serial.print(F("CO2 "));
    Serial.print(ppm);
    Serial.println(F(" ppm"));
  }
}



/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
   ###################################################################################################### 
        BLOQUE DE FUNCIONES: LECTURAS DE SENSORES, COMUNICACION SERIE, CONTROL LCD...
   ###################################################################################################### 
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
//    MQ135
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

//========================================================
//  FUNCION PARA CALIBRAR EL MQ135 PARA CO2
//========================================================

unsigned long calibrarCO2()
{          
  float Rsensor_media = 0;                    //variable usada para la calibracion
  int iteraciones  = 0;                       //para el control visual del progreso ....
  unsigned long inicio = millis();
  
  Serial.println(F("Calibrando Sensor..."));
  
  while(millis()-inicio < 300000){            //5 minutos aproximadamente
    int adc = lecturaSensorMQ(PIN_MQ135);
    float Rsensor = (1024*(20000.0/adc))-20000;
    Rsensor_media += Rsensor;
    iteraciones++;
    delay(1000);
    Serial.print(F("."));
    if(iteraciones%30==0){
      Serial.println();
    }
  }
  Serial.println(F("\n>> Calibracion Terminada <<\n"));

  /* calculo de Ro en funcion de la Rs media durante 5 minutos a una concentracion de CO2 conocida */
  Rsensor_media /= iteraciones;

  unsigned long ro = Rsensor_media/(a*pow(PPM_REFERENCIA, b));  //ppm=410 ( ¿la media mundial actual? )

  /* mostrar los datos calculados */
  Serial.print(F("Ro (calibrada) = "));Serial.println(ro);
  Serial.println("");
  return ro;
}


//========================================================
//  FUNCION OBTENER EL VALOR DE CO2
//========================================================

int medirCO2(uint8_t pin)
{ 
  /* lectura el CO2 desde el MQ135*/
  int adc = lecturaSensorMQ(pin);
  float Rsensor = (1024*(20000.0/adc))-20000;
  int ppm = pow((Rsensor/Ro)/a,(1/b)); // 'a' y 'b', constantes del sensor. 'Ro',  valor calculado previamente
  return ppm;
}


//========================================================
//  FUNCION PARA OBTENER LECTURAS DEL ADC DE UN MQxxx
//========================================================

int lecturaSensorMQ(uint8_t pin)
{
  /* hacemos el promedio de 8 muestras consecutivas */
  int analogica_MQ = 0;
  for(int i=0;i<8;i++){  //leemos 8 veces y hacemos la media
    analogica_MQ += analogRead(pin);
    delay(2);
  }
  analogica_MQ = analogica_MQ >> 3; // division por 8 (con desplazamiento de 3 bits)        
  return analogica_MQ; 
}



//*******************************************************
//                    FIN DE PROGRAMA
//*******************************************************
