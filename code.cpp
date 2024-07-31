#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include <SimpleTimer.h>

 float left ;
 float timer  ;


float calibration_value = 21.66; //21.34 - 0.7
int phval = 0; 
unsigned long int avgval; 
int buffer_arr[10],temp;

float ph_act;
// for the OLED display

////////////////////////////////////////////////////////////////////////////////////////////::::
#define TdsSensorPin 32
#define VREF 3.3              // analog reference voltage(Volt) of the ADC
#define SCOUNT  30            // sum of sample point

int analogBuffer[SCOUNT];     // store the analog value in the array, read from ADC
int analogBufferTemp[SCOUNT];
int analogBufferIndex = 0;
int copyIndex = 0;

float averageVoltage = 0;
float tdsValue = 0;
float temperature = 25;       // current temperature for compensation

// median filtering algorithm
int getMedianNum(int bArray[], int iFilterLen){
  int bTab[iFilterLen];
  for (byte i = 0; i<iFilterLen; i++)
  bTab[i] = bArray[i];
  int i, j, bTemp;
  for (j = 0; j < iFilterLen - 1; j++) {
    for (i = 0; i < iFilterLen - j - 1; i++) {
      if (bTab[i] > bTab[i + 1]) {
        bTemp = bTab[i];
        bTab[i] = bTab[i + 1];
        bTab[i + 1] = bTemp;
      }
    }
  }
  if ((iFilterLen & 1) > 0){
    bTemp = bTab[(iFilterLen - 1) / 2];
  }
  else {
    bTemp = (bTab[iFilterLen / 2] + bTab[iFilterLen / 2 - 1]) / 2;
  }
  return bTemp;
}

/////////////////////////////////////////////////////////////////////////////////////
const int trigPin = 16;
const int echoPin = 15;

float duration, distance;

int pump = 12 ;
int light = 27 ; 

int light_val ; 

#include "ArduinoJson.h"
#include <Arduino_JSON.h> 
#include "DHT.h" 
#include <WiFi.h>
String payload ;
#include <HTTPClient.h>
/////////////////////////////////////////////////////////////////////////////////
#define DHTPIN 26     // Digital pin connected to the DHT sensor
#define DHTTYPE DHT22   // DHT 22  (AM2302), AM2321
DHT dht(DHTPIN, DHTTYPE);
float t ;
float h  ;
///////////////////////////////////////
const char* ssid = "DJAWEB";
const char* password = "89072323";
char jsonOutput [128];
///////////////////////////////////////

void setup() {
  pinMode(0, OUTPUT);
  pinMode(35,INPUT);
  pinMode(TdsSensorPin,INPUT);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(pump,OUTPUT);
  pinMode(34,INPUT);
  Serial.println(F("DHTxx test!"));
  dht.begin();

  Serial.begin(115200);
  WiFi.begin(ssid, password);
  Serial.println("Connecting");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.print("\nConnected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());
 
}
 
void loop() {

light_val = analogRead(34) ;

    Serial.println(light_val);
ph();
     sending_data() ;

    receiving_data() ; 
    tds() ;

    delay(1000);


}


void tempp() {
  delay(200);

  float h = dht.readHumidity();
  // Read temperature as Celsius (the default)
  t = dht.readTemperature();
  // Read temperature as Fahrenheit (isFahrenheit = true)
  float f = dht.readTemperature(true);

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t) || isnan(f)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }


  float hif = dht.computeHeatIndex(f, h);
  // Compute heat index in Celsius (isFahreheit = false)
  float hic = dht.computeHeatIndex(t, h, false);

 /* Serial.print(F("Humidity: "));
  Serial.print(h);
  Serial.print(F("%  Temperature: "));
  Serial.print(t);
  Serial.print(F("°C "));
  Serial.print(f);
  Serial.print(F("°F  Heat index: "));
  Serial.print(hic);
  Serial.print(F("°C "));
  Serial.print(hif);
  Serial.println(F("°F"));*/
}
void sending_data(){

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient client;
    client.begin("http://192.168.1.7:5555/api/sensors");
    client.addHeader("Content-Type", "application/json");
    tempp() ;
    water_level() ;
    JSONVar postData;
    postData["id"] = "12";
   postData["temp"] = float(t) ;
    postData["humidity"] = float(t*2.44) ;
    postData["level"] = distance ;
    postData["light"] = light_val ;
    postData["tds"] = tdsValue ;
    postData["ph"] = ph_act ;
    postData["left"] = left ;
    // Convert JSON object to string
    String jsonString = JSON.stringify(postData);
    // Send POST request with JSON data
    int httpResponseCode = client.POST(jsonString);

    if (httpResponseCode > 0) {
      if (httpResponseCode == HTTP_CODE_OK) {
         payload = client.getString();
        Serial.print("Response: ");
        Serial.println(payload);
      } else {
        Serial.print("HTTP request failed with error code: ");
        Serial.println(httpResponseCode);
      }
    } else {
      Serial.println("Connection failed");
    }
  }
  else {
    Serial.println("WiFi not connected");
  }
  
}

void receiving_data(){
  
  Serial.println("Parsing start: ");
 
  JsonDocument doc;                         //Memory pool
  deserializeJson(doc, payload);//Parse message

  //Get sensor type value
  int value = doc["timer"];    
            //Get value of sensor measurement

  int state =    doc["state"];    

  Serial.print("state");
  Serial.println(state);      

  digitalWrite(pump_water,state);

  Serial.print("timer is  ");
  Serial.println(value*1000*3600);
  timer = millis() ;
Serial.println(timer);
 if(timer > value*1000*3600){
   digitalWrite(0,LOW);
 }
 else{
   digitalWrite(0,HIGH);
 }
  left = ((value*1000*3600) -(timer) )/1000/3600 ;
  Serial.print("left");
  Serial.println(left);

   

}


void water_level(){
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = (duration*.0343)/2;
  //Serial.print("Distance: ");
  //Serial.println(distance);
  delay(100);
}
void tds(){
    static unsigned long analogSampleTimepoint = millis();
  if(millis()-analogSampleTimepoint > 40U){     //every 40 milliseconds,read the analog value from the ADC
    analogSampleTimepoint = millis();
    analogBuffer[analogBufferIndex] = analogRead(TdsSensorPin);    //read the analog value and store into the buffer
    analogBufferIndex++;
    if(analogBufferIndex == SCOUNT){ 
      analogBufferIndex = 0;
    }
  }   
  
  static unsigned long printTimepoint = millis();
  if(millis()-printTimepoint > 800U){
    printTimepoint = millis();
    for(copyIndex=0; copyIndex<SCOUNT; copyIndex++){
      analogBufferTemp[copyIndex] = analogBuffer[copyIndex];
      
      // read the analog value more stable by the median filtering algorithm, and convert to voltage value
      averageVoltage = getMedianNum(analogBufferTemp,SCOUNT) * (float)VREF / 4096.0;
      
      //temperature compensation formula: fFinalResult(25^C) = fFinalResult(current)/(1.0+0.02*(fTP-25.0)); 
      float compensationCoefficient = 1.0+0.02*(temperature-25.0);
      //temperature compensation
      float compensationVoltage=averageVoltage/compensationCoefficient;
      
      //convert voltage value to tds value
      tdsValue=(133.42*compensationVoltage*compensationVoltage*compensationVoltage - 255.86*compensationVoltage*compensationVoltage + 857.39*compensationVoltage)*0.5;
      
      //Serial.print("voltage:");
      //Serial.print(averageVoltage,2);
      //Serial.print("V   ");
      //Serial.print("TDS Value:");
      //Serial.print(tdsValue,0);
      //Serial.println("ppm");
    }
  }
}
void ph() {
  
   
 for(int i=0;i<10;i++) 
 { 
 buffer_arr[i]=analogRead(35);
 delay(30);
 }
 for(int i=0;i<9;i++)
 {
 for(int j=i+1;j<10;j++)
 {
 if(buffer_arr[i]>buffer_arr[j])
 {
 temp=buffer_arr[i];
 buffer_arr[i]=buffer_arr[j];
 buffer_arr[j]=temp;
 }
 }
 }
 avgval=0;
 for(int i=2;i<8;i++)
 avgval+=buffer_arr[i];
 float volt=(float)avgval*3.3/4096.0/6;  
 //Serial.print("Voltage: ");
 //Serial.println(volt);
  ph_act = -5.70 * volt + calibration_value;
 
// Serial.print("pH Val: ");
 //Serial.println(ph_act);
 
 delay(1000);
}
