## CALIBRACION DE SONDA DE PH

 - Utilidad para calibracion 'Cero' del sensor de PH


   MODO DE EMPLEO:
   
 =======================
 
  1- Quita la sonda de ph y cortocircuita los terminales del sensor.
  
  2- Ahora, ajusta el potenciometro hasta que 'V Ph' sea 2.5.
  
  3- Una vez ajustado, coloca la sonda y obten 'ADC' para dos medios de los que conozcas el PH.
     Apunta esos valores para no olvidarlos.
    
  4- Usa esos 2 valores PH y sus correspondientes de 'ADC' 
     para sustituirlos en la ecuacion de la rutina de la sonda 'medir_ph()'.

  5- Pon el codigo modificado en arduino y realiza medidas sobre esas muestras
     con valores de ph conocidos para asegurarte de que obtienes los resultados esperados(*).
     Si es asi tu sonda ya esta calibrada. En caso contrario revisa cables y/o repite el proceso.
    
     (*) Recuerda, no te preocupes si obtienes pequeñas variaciones. Son sensores no profesionales.
    
