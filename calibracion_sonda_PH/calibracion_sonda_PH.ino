/*
#       _\|/_   A ver..., ¿que tenemos por aqui?
#       (O-O)        
# ---oOO-(_)-OOo---------------------------------
 
 
##########################################################
# ****************************************************** #
# *          LABORATORIO PARA PRINCIPIANTES            * #
# *           Calibracion de sonda para Ph             * #
# *          Autor:  Eulogio López Cayuela             * #
# *                                                    * #
# *  Calibracion sonda Ph v1.0     Fecha: 06/07/2019   * #
# ****************************************************** #
##########################################################
*/


#define __VERSION__ "Utilidad para calibrar el sensor PH\n"


/*
      ===== NOTAS DE LA VERSION "ZANGANO" ===== 

 - Utilidad para calibracion 'Cero' del sensor de PH


   MODO DE EMPLEO:
 =======================
  1- Quita la sonda de ph y cortocircuita los terminales del sensor
  2- Ahora, ajusta el potenciometro hasta que 'V Ph' sea 2.5  
  3- Una vez ajustado, coloca la sonda y obten 'ADC' para dos medios de los que conozcas el PH.
     Apunta esos valores para no olvidarlos.
    
  4- Usa esos 2 valores PH y sus correspondientes de 'ADC' 
     para sustituirlos en la ecuacion de la rutina de la sonda 'medir_ph()'.

  5- Pon el codigo modificado en arduino y realiza medidas sobre esas muestras
     con valores de ph conocidos para asegurarte de que obtienes los resultados esperados(*).
     Si es asi tu sonda ya esta calibrada. En caso contrario revisa cables y/o repite el proceso.
    
     (*) Recuerda, no te preocupes si obtienes pequeñas variaciones. Son sensores no profesionales.
    


  CONEXIONES:
 =======================
  ARDUINO UNO   SENSOR PH
 =======================
  GND               GND
  5V                Vcc
  A1                P0


    Tamaño actual compilado 4782 bytes de ROM y 212 bytes de RAM

*/




/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
//        IMPORTACION DE LIBRERIAS 
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/
//nada para ese montaje


/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
//        CREACCION DE OBJETOS
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/
//nada para ese montaje


/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
//        SECCION DE DECLARACION DE CONSTANTES  Y  VARIABLES GLOBALES
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

//------------------------------------------------------------------------
// Algunas definiciones personales para mi comodidad al escribir codigo
//------------------------------------------------------------------------
#define AND      &&
#define OR       ||
#define NOT       !
#define ANDbit    &
#define ORbit     |
#define NOTbit    ~
#define XORbit    ^


//------------------------------------------------------
//Otras definiciones para pines y variables
//------------------------------------------------------
#define PIN_LED_OnBoard    13                   // Led on Board de las placas arduino
#define PIN_SENSOR_PH      A1                   // pin analogico para la sonda de ph

float VPH = 0.0;                                // voltaje asociado a la medida del ADC (util para la calibracion)
float VALOR_ADC = 0.0;                          // Valor del conversor ADC (util para la calibracion)

unsigned long momento_para_adquirir_datos = 0;  // para controlar el momento de tomar muestras



/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
   ****************************************************************************************************** 
                                    FUNCION DE CONFIGURACION
   ****************************************************************************************************** 
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

void setup()
{
  Serial.begin(115200);               // iniciar el puerto serie
  //delay(10000);                     // descomentar con arduino MICRO, o no da tiempo a mostrar los mensajes de setup
  Serial.println (F(__VERSION__));    // mostramos la version por consola, DEBUG

  pinMode(PIN_LED_OnBoard, OUTPUT);   // PIN_LED_OnBoard como salida
  digitalWrite(PIN_LED_OnBoard, LOW); // apagamos el led 'On Board'

  /* mostar instrucciones */
  Serial.println (F("1. Quita la sonda de ph y cortocircuita los terminales del sensor")); 
  Serial.println (F("2. Ahora, ajusta el potenciometro hasta que 'V Ph' sea 2.5\n")); 
  
  Serial.println (F("3. Una vez ajustado, coloca la sonda y obten 'ADC' ")); 
  Serial.println (F("   para dos medios de los que conozcas el PH\n")); 
  
  Serial.println (F("4. Usa esos 2 valores de PH y sus correspondientes de 'ADC'")); 
  Serial.println (F("   para sustituirlos en la ecuacion de la rutina de la sonda")); 
  Serial.println (F("n\n"));
  delay(10000);
}



/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
   ****************************************************************************************************** 
                                  BUCLE PRINCIPAL DEL PROGRAMA
   ****************************************************************************************************** 
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/

void loop()
{ 
  /* mostrar informacion durante el proceso de calibracion */
  unsigned long momento_actual = millis();
  if (momento_actual > momento_para_adquirir_datos){
    momento_para_adquirir_datos = momento_actual + 4000;    //una muestra cada 4 segundos
    float PH = medir_ph();
    Serial.print(F("Ph: "));Serial.println(PH);
    Serial.print(F("V Ph: "));Serial.println(VPH);
    Serial.print(F("ADC: "));Serial.println(VALOR_ADC);
    Serial.println(F("---------------------------"));
  }
}



/*mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
   ###################################################################################################### 
        BLOQUE DE FUNCIONES: LECTURAS DE SENSORES, COMUNICACION SERIE, CONTROL LCD...
   ###################################################################################################### 
//mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm*/


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
  
  /* toma de muestras desde la sonda */
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
  
  VALOR_ADC = valor_medio;    //copiado a la variable global para usarlo en la calibracion

  /* obtener el voltaje asociado a la lectura del pin analogico (util para la calibracion de 'CERO') */
  float Vph = valor_medio*5.0/1023; 
  VPH = Vph;                  //copiado a la variable global para usarlo en la calibracion

  /* calculo del PH usando dos medidas de ph conocidas para calibrar */
  float ph_bajo = 3.4;        // Vinagre, ph = 3.4
  float adc_ph_bajo = 617;    // valor ADC para ph = 3.4          (ph obtenidos con papel tornasol)

  
  float ph_alto = 8;          // Agua del grifo, ph = 8
  float adc_ph_alto = 463;    // valor ADC para ph = 8  
  
  float PH2 = (valor_medio - adc_ph_alto ) * ((ph_alto-ph_bajo) / ( adc_ph_alto - adc_ph_bajo )) + ph_alto;

  /* Si se desea, aqui podemos controlar la validez de los datos antes de devolverlos */
  if(PH2>=0 AND PH2<=14){
    //Serial.print(F("PH = "));
    //Serial.println(PH2, 2);
  }
  else{
    //Serial.println(F("ERROR - Revise la sonda"));
    //PH2 = -100;
  }
  return PH2;
}



//*******************************************************
//                    FIN DE PROGRAMA
//*******************************************************
