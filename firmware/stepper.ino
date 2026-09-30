// ESP32 + L293D + NEMA17

#define IN1 12
#define IN2 14
#define IN3 13
#define IN4 27

int stepDelay = 5;   // Smaller = faster

// Full-step sequence
int sequence[4][4] = {
  {1, 0, 1, 0},
  {0, 1, 1, 0},
  {0, 1, 0, 1},
  {1, 0, 0, 1}
};

void setup() {
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
}

void loop() {

  // Rotate continuously
  for (int step = 0; step < 4; step++) {

    digitalWrite(IN1, sequence[step][0]);
    digitalWrite(IN2, sequence[step][1]);
    digitalWrite(IN3, sequence[step][2]);
    digitalWrite(IN4, sequence[step][3]);

    delay(stepDelay);
  }
}