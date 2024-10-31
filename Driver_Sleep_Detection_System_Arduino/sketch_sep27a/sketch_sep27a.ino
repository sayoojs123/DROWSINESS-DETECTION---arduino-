const int buzzer_Pin = 7;
const int led_Pin = 9;
char sleep_status = 0;

void setup() {
  Serial.begin(9600);  // Initialize serial communication at 9600 baud
  pinMode(buzzer_Pin, OUTPUT);
  pinMode(led_Pin, OUTPUT);
  digitalWrite(buzzer_Pin, LOW);  // Ensure the buzzer is initially off
  digitalWrite(led_Pin, LOW);     // Ensure the LED is initially off
}

void loop() {
  // Check if there is serial data available from the Python program
  while (Serial.available() > 0) {
    sleep_status = Serial.read();  // Read the incoming data
    if (sleep_status == 'a') {
      // If 'a' is received, trigger the buzzer and LED
      digitalWrite(buzzer_Pin, HIGH); 
      digitalWrite(led_Pin, HIGH);
      delay(2000);  // Keep the buzzer and LED on for 2 seconds
      digitalWrite(buzzer_Pin, LOW); 
      digitalWrite(led_Pin, LOW);
      delay(100);  // Short delay before checking again
    } else if (sleep_status == 'b') {
      // If 'b' is received, keep the buzzer and LED off
      digitalWrite(buzzer_Pin, LOW); 
      digitalWrite(led_Pin, LOW);
      delay(2000);  // Ensure there's no unnecessary flickering
    }
  }
}
