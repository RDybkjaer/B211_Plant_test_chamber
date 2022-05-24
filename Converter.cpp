/*
   Denne del af koden er til at definere de funktioner og variable de forskellige classes har
   Vi har den overordnede class Modul hvor der så er fire subclasses der arver alle Moduls egenskaber
*/

#include "Wire.h"
#include "Converter.h"
const float minMaxDepth[2] = {0, 10};
const float minMaxPH[2] = {0, 10};
const float minMaxSubstrateMoisture[2] = {0, 10};
const float minMaxWaterTemperature[2] = {0, 10};
const float minMaxAirTemperature[2] = {0, 10};

Modul::Modul(byte address) {
  this->address = address;
}
void Modul::locate() {
  Wire.beginTransmission(this->address); // wake up PCF8591
  if (Wire.endTransmission() == 0) {
    Serial.println("Device " + String(address) + " found:");
  } else {
    Serial.println("Device not found");
  }
}
void Modul::byteWrite(int value) {
  Wire.beginTransmission(this->address); // wake up
  Wire.write(0b1000000); // control byte - turn on DAC
  Wire.write(value); // value to send to DAC
  Wire.endTransmission();
}
byte Modul::byteRead(int nr) {
  Wire.beginTransmission(this->address); // wake up
  Wire.write(0b1000000 + nr); // control byte - read ADC
  Wire.endTransmission();
  Wire.requestFrom(this->address, 2);
  byte a = Wire.read();
  a = Wire.read();
  return (a);
}

LysModul::LysModul(byte address): Modul(address) {}
float LysModul::readLux() {
  float a = (this->byteRead(0) + this->byteRead(1) + this->byteRead(2) + this->byteRead(3)) / 4 + minMaxLux[0];
  a = 20.54 * pow(a, 5) - 121.7 * pow(a, 4) + 275.8 * pow(a, 3) - 255.2 * pow(a, 2) + 125.6 * a - 5.343;
  Serial.println("Read:" + String(a) + "Lux");
  return a;
}
void LysModul::writeLux(float L) {
  float U = 4.646*10^(-14)*L^5 - 1.439*10^(-10)*L^4 + 1.662*10^(-7)*L^3 - 8.939*10^(-5)*L^2 + 0.02367*L + 0.07605
  this->byteWrite(toInt(U*256/3.3));
  Serial.println("Wrote:" + String(a) + "Lux in units");
}

VandModul::VandModul(byte address): Modul(address) {}
float VandModul::readDepth() {
  float prUnit = (minMaxDepth[0] - minMaxDepth[1]) / 256;
  float a = this->byteRead(3) * prUnit + minMaxDepth[0];
  Serial.println("Read:" + String(a) + "Depth");
  return a;
}
float  VandModul::readpH() {
  float prUnit = (minMaxPH[0] - minMaxPH[1]) / 256;
  float a = this->byteRead(2) * prUnit + minMaxDepth[0];
  Serial.println("Read:" + String(a) + "pH");
  return a;
}
float VandModul::readMoisture() {
  float prUnit = (minMaxSubstrateMoisture[0] -  minMaxSubstrateMoisture[1]) / 256;
  float a = this->byteRead(1) * prUnit + minMaxDepth[0];
  Serial.println("Read:" + String(a) + "Moisture");
  return a;
}
void VandModul::writeDepth(float value) {
  float prUnit = (minMaxDepth[0] - minMaxDepth[1]) / 256;
  byte a = value / prUnit;
  this->byteWrite(a);
  Serial.println("Wrote:" + String(a) + "Depth in units");
}


TempModul::TempModul(byte address): Modul(address) {}
float TempModul::readWater() {
  float prUnit = (minMaxWaterTemperature[0] -  minMaxWaterTemperature[1]) / 256;
  float a = this->byteRead(3) * prUnit + minMaxDepth[0];
  Serial.println("Read:" + String(a) + "Moisture");
  return a;
}
float TempModul::readAir() {
  float U = -0.017(1.42*pow(10,7)*U-3.87*pow(10,8)+sqrt(1.47*pow(10,14)*U^2-9.51*10^15*U+1.5*10^17))/(73*U-1980)
  float a = this->byteRead(4) * prUnit + minMaxDepth[0];
  Serial.println("Read:" + String(a) + "Moisture");
  return a;
}
void TempModul::writeTemp(float T) {
  float U = -60*(-8.33*10^22*T^2 + 1*10^14*sqrt(-1.32*10^42*T^2 - 8.75*10^45*T + 6.28*10^65) - 5.52*10^26*T + 7.92*10^46)/(1.84*10^23*T^2 + 1.22*10^27*T + 5.46*10^29)
  this->byteWrite(toInt(U*256/3.3));
  Serial.println("Wrote:" + String(a) + "Temperature in units");
}
