/*
#       _\|/_   A ver..., ¿que tenemos por aqui?
#       (O-O)        
# ---oOO-(_)-OOo---------------------------------
 
 
##########################################################
# ****************************************************** #
# *          LABORATORIO PARA PRINCIPIANTES            * #
# *  Reproducir en casa el experimento bioclimatico    * #
# *    hecho en el biotecnoencuentro Pulpi 10/2019     * #
# *          Autor:  Eulogio López Cayuela             * #
# *                                                    * #
# *       Mini tierra v1.0   Fecha: 02/11/2019         * #
# ****************************************************** #
##########################################################
*/


#define __VERSION__ "MINI TIERRA: Experimento Bioclimatico\n"


/*
      ===== NOTAS DE LA VERSION "ZANGANO" ===== 
   
 - Version minimalista que pasa todo el trabajo al software python
   y que se limita a servir de interfaz para la adquisicion de datos


   >> Fecha: 02/11/2019
 - Calibrado del sensor de gases MQ135 para usarlo con CO2
   Se realiza la calibracion ante un entorno cpn concentracion conocida.
   (Usaremos alrededor de  415ppm que es lo que se estima de media ahora mismpo en el planeta)

 - Calibrado del sensor de PH con dos soluciones conocidas, Agua del grifo ph 8.0 y vinagre ph 3.4

 - El experimento dispondra de sensor de CO2, PH Temperatura y Humedad en el interior del recipiente
   Asi misno tendremos disponibles la temepratura y la presion atmosferica en el entorno del experimento
   


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


 =======================
  ARDUINO UNO      GY-21
 =======================
  GND               GND
  5V                Vin
  SCL (A5)          SCL
  SDA (A4)          SDA


 =======================
  ARDUINO UNO   SENSOR PH
 =======================
  GND               GND
  5V                Vcc
  A1                P0


 =======================
  ARDUINO UNO   BMP180
 =======================
  GND               GND
  5V                Vcc
  SCL (A5)          SCL
  SDA (A4)          SDA


 (Led OPCIONAL, no usado en este montaje)
 =======================
  ARDUINO        LED  
 =======================
  GND         GND del led
  A2          led


    Tamaño actual compilado 9680 bytes de ROM y 515 bytes de RAM

*/




/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
//        IMPORTACION DE LIBRERIAS 
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/
#include <Wire.h>
#include <Adafruit_HTU21DF.h>         //ojo esta libreria tal cual falla con algunos sensores clonicos
#include <SFE_BMP180.h>               //biblioteca para el sensor de presion y temperatura

/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
//        CREACCION DE OBJETOS
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

/* Objeto higrometro basado en el HTU21DF */
Adafruit_HTU21DF Higrometro_GY_21 = Adafruit_HTU21DF();

/* Objeto barometro basado en el BMP180 */
SFE_BMP180 sensorBMP180; 


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
#define PIN_LED_OnBoard    13           // Led on Board
#define PIN_MQ135          A0           //pin al que se conecta nuestro sensor MQxx

#define PIN_SENSOR_PH      A1           //pin del la sonda de Ph
#define PIN_led            A2           //led opcional, para medir luminosidad


#define ALTITUD   407.0
float PresionABS = -100;				        //inicializado fuera de rango (sin uso por ahora)
float PresionRelativaCotaCero = -100;	  //inicializado fuera de rango
float TEMPERATURA_ext = -100;  			    //inicializado fuera de rango

float TEMPERATURA_int = -100;           //inicializado fuera de rango
float HUMEDAD_int = -100;               //inicializado fuera de rango

int PPM = -100;                         //inicializado fuera de rango
float PH = -100;                        //inicializado fuera de rango
int LUZ = -100;                         //inicializado fuera de rango (sin uso por ahora)



unsigned long momento_para_adquirir_datos = 0;  //para controlar el momento de tomar muestras


float a = 5.5973021420;         //a y b   constantes del sensor para medidas de CO2
float b = -0.365425824;         //obtenidas de su hoja de caracteristicas

unsigned long Ro = 522522;      //Ro  del sensor que se ha de calcular calibrandolo. 
                                //Se usa este valor si no se activa la calibracion
#define PPM_REFERENCIA  415     //ppm del ambiente de calibracion



/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
   ****************************************************************************************************** 
                                    FUNCION DE CONFIGURACION
   ****************************************************************************************************** 
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

void setup()
{
  Serial.begin(115200);                           //iniciar el puerto serie
  //delay(10000);                                 //descomentar con arduino MICRO, o no veras los mensajes de setup
  Serial.println (F(__VERSION__));                //mostramos la version por consola, DEBUG
  //Serial.print(F("Ro (referencia) = "));
  //Serial.println(Ro);                           //mostrar el valor Ro usado como referencia si no hay calibracion
  
  /* Inicializacion del higrometro */  
  if (!Higrometro_GY_21.begin()) {
    Serial.println(F("Sensor HTU no presente"));  //si tienes un sensor clonico, puedes ver este mensaje siempre
    //while (true);                               //saltamos este punto porque sensores clon no responden correctamente
  }
  
  /* Inicializacion del barometro BMP180 */
  if (sensorBMP180.begin()){
    Serial.println(F("BMP180 iniciado"));
  }
  
  pinMode(PIN_LED_OnBoard, OUTPUT);       //pin led OnBoard como salida
  digitalWrite(PIN_LED_OnBoard, LOW);     //apagamos el led 'On Board'

  
  leerSensores();     //refresco inicial de las variables
}



/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
   ****************************************************************************************************** 
                                  BUCLE PRINCIPAL DEL PROGRAMA
   ****************************************************************************************************** 
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

void loop()
{ 
  /* mostrar medidas resales en funcion de la calibracion */
  unsigned long momento_actual = millis();
  if (momento_actual > momento_para_adquirir_datos){
    momento_para_adquirir_datos = momento_actual + 5000;    // refresca los valortes cada 5 segundos
    leerSensores();
    //mostarDatosEnPython();    //descomentar si deseamos monitorizar por puerto serie, sin conexion PC/Raspi
  }
  leerPuertoSerie();            //mostraremos los datos solo si hay peticiones por puerto serie
}



/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
   ###################################################################################################### 
        BLOQUE DE FUNCIONES: LECTURAS DE SENSORES, COMUNICACION SERIE, CONTROL LCD...
   ###################################################################################################### 
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
//    RECOPILAR DATOS DE LOS SENSORES
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

//========================================================
//  FUNCION BASE PARA OBTENER DATOS DESDE LOS SENSORES
//========================================================

void leerSensores()
{ 
  /* leer datos desde el sensor de humedad y temperatura  GY-21 - HTU21DF*/
  TEMPERATURA_int = Higrometro_GY_21.readTemperature();

  //filtrado de datos de humedad apra eliminar 'fantasmas'
  HUMEDAD_int = Higrometro_GY_21.readHumidity();
  if(HUMEDAD_int<0){
	  HUMEDAD_int = 0;
  }
  if(HUMEDAD_int>100){
	  HUMEDAD_int=100;
  }
  
  /* medir valor de PH */
  PH = medir_ph();
  
  /* lectura el CO2 desde el MQ135*/
  PPM = medirCO2(PIN_MQ135);

  /* Lectura del BMP180 */
  obtenerDatosSensorBMP180();  //se asignan directamente a variables globales

  /* medir luminosidad con un led*/
  //LUZ = analogRead(PIN_led);
}


/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
//    MQ135
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

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


/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
//    SENSOR DE PH
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

//========================================================
//  OBTENER DATOS DESDE EL SENSOR ANALOGICO DE PH
//========================================================

float medir_ph() 
{
  int buffer_lecturas[10];
  int temp;
  
  /* toma de muestras */
  for(int i=0;i<10;i++) { 
    buffer_lecturas[i] = analogRead(PIN_SENSOR_PH);
    delay(100);
  }
  
  /* ordenar las muestas de menor a mayor */
  for(int i=0;i<9;i++){
    for(int j=i+1;j<10;j++){
      if(buffer_lecturas[i]>buffer_lecturas[j]){
        temp=buffer_lecturas[i];
        buffer_lecturas[i]=buffer_lecturas[j];
        buffer_lecturas[j]=temp;
      }
    }
  }

  /* calcular el valor medio despreciando los dos valores menores y los dos mayores */
  float valor_medio = 0; 
  for(int i=2;i<8;i++){
    valor_medio+=buffer_lecturas[i];
  }

  valor_medio = valor_medio/6;

  /* obtener el voltage asociado a la lectura del pin analogico (sin utilidad por ahora) */
  //float Vph = valor_medio*5.0/1023;  

  /* ---  calculo del PH usando dos medidas de ph conocidas para calibrar --- */
  float ph_bajo = 3.4;        // Vinagre, ph = 3.4
  float adc_ph_bajo = 617;    // valor ADC para ph = 3.4          (ph obtenidos con papel tornasol)

  
  float ph_alto = 8;          // Agua del grifo, ph = 8
  float adc_ph_alto = 463;    // valor ADC para ph = 8 
  
  float PH2 = (valor_medio - adc_ph_alto ) * ((ph_alto-ph_bajo) / ( adc_ph_alto - adc_ph_bajo )) + ph_alto;

  if(PH2>=0 AND PH2<=14){
    //Serial.print(F("PH = "));
    //Serial.println(PH2, 2);
  }
  else{
    //Serial.println(F("ERROR - Revise la sonda"));
    PH2 = 0;  //( -100, valor fuera de rango)
  }
  return PH2;
}


/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
//    BAROMETRO 
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

//========================================================
//  BAROMETRO, usando sensor BMP180
//========================================================
void obtenerDatosSensorBMP180()
{
  char estado;
  double T,P,p0,a;
  boolean FLAG_fallo_BMP180 = false;
  
  /* 
   * Primero se debe hacer una lectura de la temepratura para poder hacer una medida de presion.
   * Se inicia el proceso de lectura de la temperatura.
   * Si se realiza sin errores, se devuelve un numero de (ms) de espera, si no, la funcion devuelve 0.
   */
  
  estado = sensorBMP180.startTemperature();
  if (estado != 0) {
    delay(estado);  // pausa para que se complete la medicion en el sensor.

    // Obtencion de la medida de temperatura que se almacena en T:
    // Si la lectura el correcta la funcion devuelve 1, si se producen errores, devuelve 0.

    estado = sensorBMP180.getTemperature(T);
    if (estado != 0) {
      TEMPERATURA_ext = T;  //Asignacion a variable global
      
      /* 
       * Se inicia el proceso de lectura de la presion.
       * El parametro para la resolucion de muestreo varia de 0 a 3 (a mas resolucion, mayor tiempo necesario).
       * Si se realiza sin errores, se devuelve un numero de (ms) de espera, si no, la funcion devuelve 0.
       */

      estado = sensorBMP180.startPressure(3);
      if (estado != 0) { 
        delay(estado); // pausa para que se complete la medicion en el sensor.
        
        // Obtencion de la medida de Presion que se almacena en P:
        // Si la lectura el correcta la funcion devuelve 1, si se producen errores, devuelve 0.
        estado = sensorBMP180.getPressure(P,T);

        if (estado != 0) {
          PresionABS = P;  //Asignacion a variable global

          /* 
           * El sensor devuelve presion absoluta. Para compensar el efecto de la altitud
           * usamos la funcion interna de la libreria del sensor llamada: 'sealevel'
           * P = presion absoluta en (mb) y ALTITUD = la altitud del punto en que estomos (m).
           * Resultado: p0 = presion compensada a niveldel mar en (mb)
           */

          p0 = sensorBMP180.sealevel(P,ALTITUD);  // 407 metros (SORBAS, La Tejica)
          PresionRelativaCotaCero = p0;           //Asignacion a variable global
        }
        else FLAG_fallo_BMP180 = true; //error en las lecturas/obtencion de datos
      }
      else FLAG_fallo_BMP180 = true;
    }
    else FLAG_fallo_BMP180 = true;
  }
  else FLAG_fallo_BMP180 = true;

  /*
   * Ante fallos de lectura del sensor barometrico establecemos valores fuera de rango
   * para facilitar la captura del error desde programas externos
   */
  if (FLAG_fallo_BMP180 == true){
    TEMPERATURA_ext = -100;
    PresionABS = -100;
    PresionRelativaCotaCero = -100;
  }
}


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
  
  int lectura = 'x';                //por defecto pensamos que no se nos pide nada
  if (Serial.available() > 0) {
     // leer byte
    lectura = Serial.read();
    if (lectura == '*' OR lectura == '+'){  // indicador para mandar una muestra unica al puerto serie
      mostarDatosEnPython();
      return 0;  //ok, peticion de datos
     } 
  }
  return -1;    //sin peticion por parte del usuario
}


//========================================================
//  ENVIAR DATOS POR PUERTO SERIE A PYTHON
//========================================================

void mostarDatosEnPython()
{ 
  Serial.flush();
  
  /* FORMATEO de datos y ENVIO al puerto SERIE */
  Serial.print(TEMPERATURA_int);
  Serial.print(F("**"));
  Serial.print(HUMEDAD_int);
  Serial.print(F("**"));
  Serial.print(PH);
  Serial.print(F("**"));
  Serial.print(PPM);
  Serial.print(F("**"));
  Serial.print(PresionRelativaCotaCero);
  Serial.print(F("**"));
  //Serial.print(LUZ);                  //sin uso en este montaje
  //Serial.print(F("**"));              //sin uso en este montaje
  Serial.println(TEMPERATURA_ext); 
}



//*******************************************************
//                    FIN DE PROGRAMA
//*******************************************************
