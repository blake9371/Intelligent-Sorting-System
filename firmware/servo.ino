#include <ESP32Servo.h>

Servo myServo;

const int servoPin = 18;

void setup() {
  Serial.begin(115200);

  myServo.attach(servoPin);
  myServo.write(90);
}

void loop() {
  if (Serial.available() > 0) {
    char input = Serial.read();

    if (input == '0') {
      myServo.write(90);
      Serial.println("Servo -> 90 degrees");
    }

    else if (input == '1') {
      myServo.write(135);
      Serial.println("Servo -> 135 degrees");
    }

    else if (input == '2') {
      myServo.write(45);
      Serial.println("Servo -> 45 degrees");
    }
  }
}