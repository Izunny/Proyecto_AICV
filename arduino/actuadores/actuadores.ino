// Librerias para la pantalla OLED
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// Macros para la pantalla OLED
#define SCREEN_WIDTH 128  // OLED display width, in pixels
#define SCREEN_HEIGHT 64  // OLED display height, in pixels
#define OLED_RESET -1     // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Librerias para el buzzer
#include <EasyBuzzer.h>

// Definición de los pines para los LEDs
const int led_rojo_1 = 2;
const int led_amarillo_1 = 3;
const int led_verde_1 = 4;
const int led_rojo_2 = 5;
const int led_amarillo_2 = 6;
const int led_verde_2 = 7;
int option;

void setup() {
  // Empieza el puerto serial a 9600 baudios
  Serial.begin(9600);

  // Leds para el semaforo 1
  pinMode(led_rojo_1, OUTPUT);
  pinMode(led_amarillo_1, OUTPUT);
  pinMode(led_verde_1, OUTPUT);
  // Leds para el semaforo 2
  pinMode(led_rojo_2, OUTPUT);
  pinMode(led_amarillo_2, OUTPUT);
  pinMode(led_verde_2, OUTPUT);
}

void loop() {
  // Función para que funcione la librería
  EasyBuzzer.update();

  if (Serial.available() > 0) {
    // Dato enviado desde el script de Python
    option = Serial.read();

    switch (option) {

      // Semaforo 1
      case '2':
        digitalWrite(led_rojo_1, HIGH);
        delay(delayT);
        digitalWrite(led_rojo_1, LOW);
        break;
      case '3':
        digitalWrite(led_amarillo_1, HIGH);
        delay(delayT);
        digitalWrite(led_amarillo_1, LOW);
        break;
      case '4':
        digitalWrite(led_verde_1, HIGH);
        delay(delayT);
        digitalWrite(led_verde_1, LOW);
        break;
        
      // Semaforo 2
      case '5':
        digitalWrite(led_rojo_2, HIGH);
        delay(delayT);
        digitalWrite(led_rojo_2, LOW);
        break;
      case '6':
        digitalWrite(led_amarillo_2, HIGH);
        delay(delayT);         
        digitalWrite(led_amarillo_2, LOW);
        break;
      case '7':
        digitalWrite(led_verde_2, HIGH);
        delay(delayT);
        digitalWrite(led_verde_2, LOW);
        break;

      // Pantalla OLED
      case '8':
        // Initialize the OLED object
        if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
          Serial.println(F("SSD1306 allocation failed"));
        for (;;); // Don't proceed, loop forever
        }
        
        // Clear the buffer
        display.clearDisplay();

        // Display Text
        display.setTextSize(1);
        display.setTextColor(WHITE);
        display.setCursor(0, 28);
        display.println("Hello world!");
        display.display();
        delay(2000);
        display.clearDisplay();
        break;

      // Buzzer
      case '9':
          Serial.begin(9600);
  
          // Configuración del pin
          EasyBuzzer.setPin(12);
          
          // Configuración del beep
          EasyBuzzer.beep(
            2000,          // Frecuencia en herzios
            100,           // Duración beep en ms
            100,           // Duración silencio en ms
            2,             // Números de beeps por ciclos
            300,           // Duración de la pausa
            1            // Número de ciclos
          );
        

      break;  
      default:
        Serial.println("Opcion no valida. Por favor, ingrese '2' para encender el LED rojo 1.");
        break;
    }
  }
}