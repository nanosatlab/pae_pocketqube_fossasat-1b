   /*
 * HelTec Automation(TM) WIFI_LoRa_32 factory test code, witch includ
 * follow functions:
 * 
 * - Basic OLED function test;
 * 
 * - Basic serial port test(in baud rate 115200);
 * 
 * - LED blink test;
 *  
 * - LoRa Ping-Pong test (DIO0 -- GPIO26 interrup check the new incoming messages);
 * 
 * - Timer test and some other Arduino basic functions.
 *
 * by Aaron.Lee from HelTec AutoMation, ChengDu, China
 * 成都惠利特自动化科技有限公司
 * https://heltec.org
 *
 * this project also realess in GitHub:
 * https://github.com/HelTecAutomation/Heltec_ESP32
*/

#include "Arduino.h"
#include "heltec.h"
#include "log.h"
#include "kiss.h"
#include "SyncBuffer.h"

#define LORA_FREQUENCY  868E6  //you can set band here directly,e.g. 868E6,915E6
#define LORA_BANDWIDTH  125E3   // Ideal 250 kHz
#define LORA_SF         8    // Ideal case: 7
#define LORA_CR         5
#define LORA_PREAMBLE_LENGTH  8
#define LORA_SYNC_WORD  0x34
#define MAX_SERIAL_SIZE 512
#define MAX_LORA_SIZE   512

int uart_speed = 500000;
SyncBuffer buffer;
/* Content structures */
uint8_t serial_msg[MAX_SERIAL_SIZE];
uint8_t lora_msg[MAX_LORA_SIZE];
uint8_t temp_msg[MAX_LORA_SIZE];
uint32_t tx_counter;
uint32_t tx_size;
uint32_t rx_counter;
uint32_t rx_size;
int rx_rssi;

void setup()
{
  /*  Always start with this to activate Heltec module.
   *  The Input parameters are: 
   *  - DispalyEnable (bool) --> enable the display of the device 
   *  - LoRaEnable (bool) --> enable to work with LoRa
   *  - SerialEnable (bool) --> enable to configure the Serial port
   *  - LoRa PABOOST (bool) --> activate the power amplifier to reach 20 dBm of TX
   *  - BAND (float) --> determines the frequency of LoRa system
   *  In our case, we have disabled the Serial port because it is managed by the 'kiss' module.
   *  Default values of the LoRa module (defined by the library itself) are:
   *  - LoRa spreading factor = 11
   *  - Bandwidth = 125 kHz
   *  - Sync word = 0x34
   *  - CRC is enabled
   *  We may have to modify them using the 'set' functions (see Heltec library).
   */
  Heltec.begin(true, true, false, true, LORA_FREQUENCY);
  LoRa.setSignalBandwidth(LORA_BANDWIDTH);
  LoRa.setSpreadingFactor(LORA_SF);
  LoRa.setCodingRate4(LORA_CR);
  LoRa.setPreambleLength(LORA_PREAMBLE_LENGTH);
  LoRa.setSyncWord(LORA_SYNC_WORD);
  LoRa.enableCrc();
  
  /* Clear display screen */
  delay(100);
  Heltec.display -> clear();
  /* Open Serial port communication with computer */
  Serial.begin(uart_speed, SERIAL_8N1);
  while(!Serial) {;}  // wait to initialize the serial
  //LOG::info("LoRa device ready to work!");
  tx_counter = 0;
  tx_size = 0;
  rx_counter = 0;
  rx_size = 0;
  rx_rssi = 0;
  onDisplay();
}


void loop()
{ 
  /* Check if something is in the serial port */
  if(Kiss::available() > 0 && Kiss::available() <= MAX_SERIAL_SIZE) {
      uint32_t readed = Kiss::read(serial_msg, Kiss::available());
      if(readed > 0){
        send(serial_msg, readed);
      }
  }
  
  /* Check if something is received from LoRa module */
  int packetSize = LoRa.parsePacket();
  if(packetSize > 0) {
    rx_rssi = LoRa.packetRssi();
    rx_size = 0;
    memset(lora_msg, 0, MAX_LORA_SIZE);
    memcpy(lora_msg, &rx_rssi, 4);
    while(LoRa.available() > 0 && rx_size < packetSize) {
        lora_msg[4 + rx_size] = LoRa.read();
        rx_size ++;
    }
    Kiss::write(lora_msg, 4 + rx_size);
    rx_counter ++;
    onDisplay();
  }
}

void send(const uint8_t *msg, uint32_t length)
{
    LoRa.beginPacket();
    LoRa.write(msg, length);
    LoRa.endPacket();
    tx_counter ++;
    tx_size = length;
    onDisplay();
}

void onDisplay()
{
  Heltec.display->clear();
  Heltec.display->drawString(0, 0, "TX Packets: ");
  Heltec.display->drawString(100, 0, String(tx_counter));
  Heltec.display->drawString(0, 10, "TX last Packet bytes: ");
  Heltec.display->drawString(100, 10, String(tx_size));
  Heltec.display->drawString(0, 30, "RX Packets: ");
  Heltec.display->drawString(100, 30, String(rx_counter));
  Heltec.display->drawString(0, 40, "RX last Packet bytes: ");
  Heltec.display->drawString(100, 40, String(rx_size));
  Heltec.display->drawString(0, 50, "RX RSSI: ");
  Heltec.display->drawString(100, 50, String(rx_rssi));
  Heltec.display->display();
}
