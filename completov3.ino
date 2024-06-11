// How many motors
#define NMOTORS 2

int r = 20; //radio de la polea conducida
bool print = 1; // poner como 1 si deseas ver pwr pos y target

// Pins
const int enca[] = {2, 3};
const int encb[] = {4, 5};
const int pwm[] = {11, 10};
const int in1[] = {13, 8};
const int in2[] = {12, 9};

// Globals
long prevT = 0;
volatile int posi[] = {0, 0};
int pos[] = {0, 0};
int target[] = {0, 0};
bool calibrado = 0;
char inputBuffer[50];
char *token;
int coordX;
int coordY;
int eprev = 0;
int eintegral = 0;
int error0 = 0;
int errorprev0 = 1;
int error1 = 0;
int errorprev1 = 1;
int pwm_max = 500;
int deltaT = 0;
int start_flag = 0;
unsigned long flag = 0;


// variables para el PID
float kp = 3; // Convert to float for better precision
float kd = 0.02; // Convert to float for better precision
float ki = 0.001; // Convert to float for better precision

void setup() {
  Serial.begin(9600);

  for (int k = 0; k < NMOTORS; k++) {
    pinMode(enca[k], INPUT);
    pinMode(encb[k], INPUT);
    pinMode(pwm[k], OUTPUT);
    pinMode(in1[k], OUTPUT);
    pinMode(in2[k], OUTPUT);
  }

  attachInterrupt(digitalPinToInterrupt(enca[0]), readEncoder<0>, RISING);
  attachInterrupt(digitalPinToInterrupt(enca[1]), readEncoder<1>, RISING);

  target[0] =  1;
  target[1] =  1;

  
}

void newtarget() {

  
  int newX = random(-200, 200);
  int newY = random(-200, 200);
   

  int X = newX - coordX;
  int Y = newY - coordY;
  //int X = 100;
  //int Y = 100;

  double A = (2 * X + 2 * Y) / (2 * r);
  double B = (2 * X - 2 * Y) / (2 * r);
  target[0] = A*15;
  target[1] = B*15;

  coordX = newX;
  coordY = newY;
}
  

void loop() {

  //Serial.println("waiting4calib");

  if(calibrado == 0 && Serial.available() > 0){
    String mensaje = Serial.readStringUntil('\n');
    //Serial.println("calibrado en proceso");
    int espacioPos = mensaje.indexOf(' '); //revisa si hay espacio

    if (mensaje=="calibrado"){
      pos[0]=0;
      pos[1]=0;
      calibrado = 1;
      Serial.println("listo calibrado");
    }

    else if (espacioPos != -1) { // Si se encontró un espacio en el mensaje
      calib(mensaje, espacioPos);

    }
    else {          //se debe eliminar para el código final
      Serial.println("mensaje no leido correctamente");
      Serial.println("listo");
    }
  }
  else if (calibrado == 1 && Serial.available() > 0){
    //waitforstart();
    Serial.print("mensaje de inicio recibido: ");
    String mensaje = Serial.readStringUntil('\n'); // Lee el mensaje hasta encontrar un salto de línea
    Serial.println(mensaje);
    pos[0] = 0;
    pos[1] = 0;
    int coordX = 0;
    int coordY = 0;  
    //delay(1000);
    start_flag=1;
  }

  while (start_flag == 1){
    

    if (error0 == errorprev0 && error1 == errorprev1) {
    newtarget();
    }

    // Read the position
    noInterrupts(); // disable interrupts temporarily while reading
    for (int k = 0; k < 2; k++) {
      pos[k] = posi[k];
    }
    interrupts(); // turn interrupts back on

    // time difference
    long currT = micros();
    float deltaT = ((float)(currT - prevT)) / (1.0e6);
    prevT = currT;

    // loop through the motors
    for (int k = 0; k < 2; k++) {
      int pwr;
      int dir;
      // evaluate the control signal
      PID(pos[k], target[k], deltaT, pwr, pwm_max, dir, k);
      // signal the motor
      setMotor(dir, pwr, pwm[k], in1[k], in2[k]);

      if (print==1){
        Serial.print(pwr);
        Serial.print(" ");
      }
    }

    if (print==1){
      Serial.print(target[0]);
      Serial.print(" ");
      Serial.print(target[1]);
      Serial.print(" ");
      Serial.print(pos[0]);
      Serial.print(" ");
      Serial.print(pos[1]);
      Serial.println();
    }

    
    if (Serial.available() > 0) {
      String msg = "";
      msg = Serial.readStringUntil('\n');
      msg.trim();
      

      if (msg == "fin"){
        //fin_programa();
        //newtarget(0,0);
        for (int k = 0; k < 2; k++) {
       
          setMotor(0, 0, pwm[k], in1[k], in2[k]);
          target[0] = 0;
          target[1] = 0;
        }
        delay(10);
        Serial.println("fin programa");
        calibrado = 0;
        start_flag = 0;
      }
    } 
    
  }
  
}

void setMotor(int dir, int pwmVal, int pwm, int in1, int in2) {
  analogWrite(pwm, pwmVal);
  if (dir == 1) {
    digitalWrite(in1, HIGH);
    digitalWrite(in2, LOW);
  } else if (dir == -1) {
    digitalWrite(in1, LOW);
    digitalWrite(in2, HIGH);
  } else {
    digitalWrite(in1, HIGH);
    digitalWrite(in2, HIGH);
  }
}


template <int j>
void readEncoder() {
  int b = digitalRead(encb[j]);
  if (b > 0) {
    posi[j]++;
  } else {
    posi[j]--;
  }
}

void PID(int value, int target, float deltaT, int &pwr, int pwm_max, int &dir, int motor) {

  int e = target - value;
  float dedt = (e - eprev) / (deltaT);
  eintegral = eintegral + e * deltaT;
  float u = kp * e + kd * dedt + ki * eintegral;

  // motor power
  pwr = (int)fabs(u);
  if (pwr > pwm_max) {
    pwr = pwm_max;
  }else if (pwr < 70 && pwr > 5) {
    pwr = 70;
  }
  else if (pwr <=5){
    pwr = 0;
  }
  
  // motor direction
  dir = 1;
  if (u < 0) {
    dir = -1;
  }else if(u == 0){
    dir = 0;
  }
  

  // Store previous error
  if (motor == 0) {
    errorprev0 = error0;
    error0 = e;
  } else if (motor == 1) {
    errorprev1 = error1;
    error1 = e;
  }

  eprev = e;
  //return (dir, pwr);
}

void calib(String mensaje, int espacioPos) {

  int pos[]={0,0};
  String numX_str = mensaje.substring(0, espacioPos);
  String numY_str = mensaje.substring(espacioPos + 1);

  // Convierte las subcadenas a enteros
  int X = numX_str.toInt();
  int Y = numY_str.toInt();
  
  double A = (2 * X + 2 * Y) / (2 * r);
  double B = (2 * X - 2 * Y) / (2 * r);
  target[0] = A*15;
  target[1] = B*15;// Create a new target array
  int est[] = {0,0};
  long currT = 0;
  int prevT = 0;
  flag = micros();//33
  
  while (true){

    noInterrupts(); // disable interrupts temporarily while reading
    for (int k = 0; k < 2; k++) {
      pos[k] = posi[k];
    }
    interrupts(); // turn interrupts back on

    // time difference
    long currT = micros();
    float deltaT = ((float)(currT - prevT)) / (1.0e6);
    prevT = currT;

   for (int k = 0; k < 2; k++) {
      int pwr =0;
      int dir =0;
      PID(pos[k], target[k], deltaT, pwr, pwm_max, dir, k);
      setMotor(dir, pwr, pwm[k], in1[k], in2[k]);

      est[k] = pwr;
    }

      //Serial.print("en loop pwr: ");
      Serial.print(est[0]);
      Serial.print(" ");
      Serial.print(est[1]);
      Serial.print(" ");
      Serial.print(target[0]);
      Serial.print(" ");
      Serial.print(target[1]);
      Serial.print(" ");
      Serial.print(pos[0]);
      Serial.print(" ");
      Serial.println(pos[1]);
      

    if ((currT/1e6)>=((flag/1e6)+1)){
      break;
    }
      

  }   

  for (int k = 0; k < 2; k++) {
    int pwr = 0;
    int dir = 0;
      
    setMotor(dir, pwr, pwm[k], in1[k], in2[k]);
  }

  pos[0] = 0;
  pos[1] = 0;     

  target[0] = 0;
  target[1] = 0;

  // Mandar un mensaje de confirmación por el puerto serial
  Serial.println("Listo");
}

int changespeed(String speed) {
  int pwm_max = 0; // Inicializamos pwm_max

  if (speed == "rapido") {
    pwm_max = 500;
  }
  else if (speed == "medio") {
    pwm_max = 300;
  }
  else if (speed == "lento") {
    pwm_max = 200;
  }

  return pwm_max;
}
