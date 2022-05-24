#include <esp_camera.h>
#include "soc/soc.h"           // Disable brownour problems
#include "soc/rtc_cntl_reg.h"  // Disable brownour problems
#include "driver/rtc_io.h"
#include <WiFi.h>
WiFiServer server(80);

const char* ssid = "HUAWEI-B535-EBEC";
const char* password = "B9Q1Y7YLE0L";
String serverName = "192.168.8.210"; //databasens url
String serverPath = "/postimg";
String apiKeyValue = "ABC123000"; //databasens adgangskode
IPAddress local_IP(192, 168, 8, 212);
IPAddress gateway(192, 168, 8, 1);
IPAddress subnet(255, 255, 0, 0);

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); //disable brownout detector
  Serial.begin(115200);
  startCam();
  delay(1000);
  WiFi.mode(WIFI_STA);
  if (!WiFi.config(local_IP, gateway, subnet)) {
    Serial.println("STA Failed to configure");
  }
  if (WiFi.begin(ssid, password)){
    Serial.println("FUCK JA WE BE FLYIIIIIN!!!!");
    Serial.println(WiFi.localIP());
  }
  server.begin();
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    Serial.println("fuck ja");
    client.println("HTTP/1.1 200 OK");
    client.println("Connection: close");
    client.println(); //blank line for header
    client.println(); //blank line for bodylient.stop();
    Serial.println("Client disconnected.");
    Serial.println("");
    client.stop();
    takePicture();
  }
}

void takePicture() {
  camera_fb_t * fb = NULL; //Sletter vi det der ligger på adressen FB
  fb = esp_camera_fb_get(); //Skriver vi fra kameraets buffer til adressen FB
  uint8_t *fbBuf = fb->buf;
  size_t fbLen = fb->len;
  WiFiClient client;
  int h = client.connect(serverName.c_str(), 8080);
  Serial.println(h);
  if (h) {
    Serial.println("nej jeg er ikke død2");
    String head = "--ESP32\r\nContent-Disposition: form-data; name=\"imageFile\"; filename=\"esp32-cam.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n";
    String tail = "\r\n--ESP32--\r\n";
    uint32_t imageLen = fb->len;
    uint32_t extraLen = head.length() + tail.length();
    uint32_t totalLen = imageLen + extraLen;

    client.println("POST " + serverPath + " HTTP/1.1");
    client.println("Host: " + serverName);
    client.println("Content-Length: " + String(totalLen));
    client.println("Content-Type: multipart/form-data; boundary=image");
    client.println();
    client.print("--image\r\nContent-Disposition: form-data; name=\"imageFile\"; filename=\"image.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n");

    for (size_t i = 0; i < fb->len; i = i + 1024) {
      if (i + 1024 < fbLen) {
        client.write(fbBuf, 1024);
        fbBuf += 1024;
        Serial.println("Banger");
      } else if (fbLen % 1024 > 0) {
        size_t remainder = fbLen % 1024;
        client.write(fbBuf, remainder);
      }
    }
    client.print("\r\n--ESP32--\r\n");
  }
  delay(1000);
  esp_camera_fb_return(fb);
}

void startCam() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 5;
  config.pin_d1 = 18;
  config.pin_d2 = 19;
  config.pin_d3 = 21;
  config.pin_d4 = 36;
  config.pin_d5 = 39;
  config.pin_d6 = 34;
  config.pin_d7 = 35;
  config.pin_xclk = 0;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sscb_sda = 26;
  config.pin_sscb_scl = 27;
  config.pin_pwdn = 32;
  config.pin_reset = -1;
  config.xclk_freq_hz = 16500000;
  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
    config.frame_size = FRAMESIZE_UXGA; // FRAMESIZE_ + QVGA|CIF|VGA|SVGA|XGA|SXGA|UXGA
    config.jpeg_quality = 4; //fra 0 til 63 lav er højere kvalitet
    config.fb_count = 2;
  }
  // Init Camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
}
