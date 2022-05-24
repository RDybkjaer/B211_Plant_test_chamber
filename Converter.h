/*
 * Denne del af koden er til at initialisere de funktioner og variable de forskellige classes har
 * Vi har den overordnede class Modul hvor der så er fire subclasses der arver alle Moduls egenskaber
 */
#ifndef Converter_h
#define Converter_h

#include "Wire.h"
#include "arduino.h"

class Modul {
  private:
    byte address;
  public:
    Modul(byte address);
    void locate();
    void byteWrite(int value);
    byte byteRead(int nr);
};

class LysModul : public Modul {
  public:
    LysModul(byte address);
    void writeLux(float L);
    float readLux();
};
class VandModul : public Modul {
  public:
    VandModul(byte address);
    void writeDepth(float value);
    float readDepth();
    float readpH();
    float readMoisture();
};
class TempModul : public Modul {
  public:
    TempModul(byte address);
    void writeTemp(float T);
    float readWater();
    float readAir();
}

#endif
