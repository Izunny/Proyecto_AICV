// Sensor Ultrasonico 1
int Trigger1=8;
int Echo1=9;  

// Sensor Ultrasonico 2
int Trigger2=10;
int Echo2=11;

// Variables para calcular la distancia 
long Duracion; 
long Distancia1;
long Distancia2; 

int sensor_magnetico_1;
int sensor_magnetico_2;

void setup() {                
  Serial.begin (9600);  
  pinMode(Echo1, INPUT);     
  pinMode(Trigger1, OUTPUT);
  pinMode(Echo2, INPUT);     
  pinMode(Trigger2, OUTPUT);     
} 

void loop() {

  // Pines analogos para los sensores magneticos
  int sensorValue1 = analogRead(A3);
  int sensorValue2 = analogRead(A2);

  // Sensor magnetico 1
  if (sensorValue1 < 500) {
    sensor_magnetico_1 = 1;
  } else {
    sensor_magnetico_1 = 0;
  }

  // Sensor magnetico 2
  if (sensorValue2 < 500) {
    sensor_magnetico_2 = 1;
  } else {
    sensor_magnetico_2 = 0;
  }


  // Sensor Ultrasonico 1
  digitalWrite(Trigger1,LOW);
  delay(4);
  digitalWrite(Trigger1,HIGH);
  delay(10);
  digitalWrite(Trigger1,LOW);
  Duracion=pulseIn(Echo1,HIGH);
  Distancia1=Duracion/58;

  // Sensor Ultrasonico 2
  digitalWrite(Trigger2,LOW);
  delay(4);
  digitalWrite(Trigger2,HIGH);
  delay(10);
  digitalWrite(Trigger2,LOW);
  Duracion=pulseIn(Echo2,HIGH);
  Distancia2=Duracion/58;

  // Imprime los valores de los sensores en el monitor serial
  Serial.print(Distancia1);
  Serial.print(" - ");
  Serial.print(Distancia2);
  Serial.print(" - ");
  Serial.print(sensor_magnetico_1);
  Serial.print(" - ");
  Serial.println(sensor_magnetico_2);

  delay(1000);
}






