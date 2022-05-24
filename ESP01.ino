/*
   Denne del af koden er til at initialisere de funktioner og variable de forskellige classes har
   Vi har den overordnede class Modul hvor der så er fire subclasses der arver alle Moduls egenskaber
*/

#include <Wire.h>
#include "Converter.h"
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESPAsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <WireSlaveRequest.h>

AsyncWebServer server(80);
const char* ssid = "HUAWEI-B535-EBEC";
const char* password = "B9Q1Y7YLE0L";
const char* serverName = "http://192.168.8.210:8080/postdata"; //databasens url
const char* imgServerName = "http://192.168.8.212";
String tablename;
String apiKeyValue = "ABC123000"; //databasens adgangskode
const int updatesPrHour = 600;
int pictureUpdateCounter = 0;
bool startUp = false; //bestemmer om vi er klar på at starte. sættes til true efter at man har modtaget hvad ting skal sættes til
IPAddress local_IP(192, 168, 8, 211);
IPAddress gateway(192, 168, 8, 1);
IPAddress subnet(255, 255, 0, 0);

LysModul lys(0b1001000);
VandModul vand(0b1001001);
TempModul temp(0b1001010);

void setup() {
  Serial.begin(74880);
  Wire.begin(2, 0);
  beginWiFiServer();
  delay(10000);
  lys.locate();
  vand.locate();
  temp.locate();
  while (startUp == false) { //Vent til den har modtaget startindstillinger
    Serial.println("Awaiting startup data...");
    delay(200);
  }
}

void loop() {
  dataSend(); //Send data men intervallet
  if (pictureUpdateCounter < 10) {
    pictureUpdateCounter++;
  } else {
    if (WiFi.status() == WL_CONNECTED) {
      WiFiClient client;
      HTTPClient http;
      http.begin(client, imgServerName);
      http.GET();
      http.end();
      Serial.println("pic has been sent");
    }
    pictureUpdateCounter = 0;
  }
  delay(3600000 / updatesPrHour);
}

void dataSend() {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    // Your Domain name with URL path or IP address with path
    Serial.println(http.begin(client, serverName));
    // Specify content-type header
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    // Prepare your HTTP POST request data
    String dataForDelivery = "api_key=" + apiKeyValue
                             + "&tablename=" + tablename
                             + "&M1=" + String("Lysmodul")
                             + "&M1S1=" + String(lys.readLux())
                             + "&M1S2=" + String(0)
                             + "&M1S3=" + String(0)
                             + "&M1S4=" + String(0)
                             + "&M2=" + String("TempModul")
                             + "&M2S1=" + String(temp.readWater())
                             + "&M2S2=" + String(temp.readAir())
                             + "&M2S3=" + String(0)
                             + "&M2S4=" + String(0)
                             + "&M3=" + String("VandModul")
                             + "&M3S1=" + String(vand.readDepth())
                             + "&M3S2=" + String(vand.readpH())
                             + "&M3S3=" + String(vand.readMoisture())
                             + "&M3S4=" + String(0)
                             + "";
    Serial.println(dataForDelivery);
    int respons = http.POST(dataForDelivery); //returnere nedern data
    if (respons > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(respons);
    }
    else {
      Serial.print("Error code: ");
      Serial.println(respons);
    }
    http.end();
  }
  else {
    Serial.println("WiFi Disconnected");
  }
}

void beginWiFiServer() {
  WiFi.mode(WIFI_STA);
  if (!WiFi.config(local_IP, gateway, subnet)) {
    Serial.println("STA Failed to configure");
  }
  //ssid, password
  WiFi.begin(ssid, password);
  server.on("/update", HTTP_GET, [](AsyncWebServerRequest * request) {
    String notPressent = "";
    String lux = "NA";
    String temperature = "NA";
    String depth = "NA";
    String uph = "NA";
    if (request->hasParam("lux")) {
      lux = String(request->getParam("lux")->value());
      lys.writeLux(lux.toFloat());
    } else {
      notPressent = notPressent + " Lux not changed ";
    }
    if (request->hasParam("temp")) {
      temperature  = String(request->getParam("temp")->value());
      temp.writeTemp(temperature.toFloat());
    } else {
      notPressent = notPressent + " Temperature not changed ";
    }
    if (request->hasParam("depth")) {
      depth  = String(request->getParam("depth")->value());
      vand.writeDepth(depth.toFloat());
    } else {
      notPressent = notPressent + " Depth not changed";
    }
    if (request->hasParam("uph")) {
      uph  = String(request->getParam("uph")->value());
    } else {
      notPressent = notPressent + " uph not changed";
    }
    if (request->hasParam("tablename")) {
      tablename = String(request->getParam("tablename")->value());
    } else {
      notPressent = notPressent + " tablename not changed";
    }
    String valueChanged = "\n Lux set to: " + lux
                          + "\n temperature set to:" + temperature
                          + "\n Depth set to: " + depth;
    + "\n UPH set to: " + uph;
    request->send(200, "text/plain", valueChanged);
    if (lux != "NA" && temperature != "NA" && depth != "NA" && uph != "NA") {
      startUp = true;
      Serial.println("has been set");
    }
  });
  server.begin();
}
