String a = "";
String test = "";

#include <SoftwareSerial.h>
#include <PN532_SWHSU.h>
#include <PN532.h>
SoftwareSerial SWSerial( 10, 11 ); // RX, TX
PN532_SWHSU pn532swhsu( SWSerial );
PN532 nfc( pn532swhsu );
void setup(void) {
  pinMode(3, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(9, OUTPUT);
//  Serial.begin(115200);
    Serial.begin(9600);
    Serial.setTimeout(1);
  // Serial.println("Hello Maker!");
  nfc.begin();
  uint32_t versiondata = nfc.getFirmwareVersion();
  Serial.println("POWER by PDAserwis");
  if (! versiondata) {
    //    Serial.print("Didn't Find PN53x Module");
    Serial.print("Error 006");
    while (1); // Halt
  }
  // Got valid data, print it out!
  //  Serial.print("Found chip PN5"); Serial.println((versiondata >> 24) & 0xFF, HEX);
  //  Serial.print("Firmware ver. "); Serial.print((versiondata >> 16) & 0xFF, DEC);
  //  Serial.print('.'); Serial.println((versiondata >> 8) & 0xFF, DEC);
  // Configure board to read RFID tags
  nfc.SAMConfig();
  //  Serial.println("Waiting for an ISO14443A Card ...");
}

void loop(void) {
 boolean success;
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };  // Buffer to store the returned UID
  uint8_t uidLength;                       // Length of the UID (4 or 7 bytes depending on ISO14443A card type)
  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, &uid[0], &uidLength);
  if (success) {
    //    Serial.println("Found A Card!");
    //    Serial.print("UID Length: ");Serial.print(uidLength, DEC);Serial.println(" bytes");
    //    Serial.print("UID Value: ");
    for (uint8_t i = 0; i < uidLength; i++)
    {
      //     Serial.print(" 0x");
      Serial.print(uid[i], HEX);
    }
    Serial.println("");
    // 2 second halt

 //   delay(2000);

  }

  else

  {

    // PN532 probably timed out waiting for a card

    //    Serial.println("Timed out! Waiting for a card...");

  }
  if (Serial.available()) {
    a = "";
    a = Serial.readStringUntil('*');
    test = "r1";
    if (test == a) {
      digitalWrite(3, HIGH);
      //     Serial.println("on");
    }
    test = "r0";
    if (test == a) {
      digitalWrite(3, LOW);
      //     Serial.println("off");
    }
    test = "b1";
    if (test == a) {
      digitalWrite(5, HIGH);
      //     Serial.println("off");
    }
    test = "b0";
    if (test == a) {
      digitalWrite(5, LOW);
      //     Serial.println("off");
    }
    test = "n1";
    if (test == a) {
      digitalWrite(6, HIGH);
      //     Serial.println("off");
    }
    test = "n0";
    if (test == a) {
      digitalWrite(6, LOW);
      //     Serial.println("off");
    }
    test = "g1";
    if (test == a) {
      digitalWrite(9, HIGH);
      //     Serial.println("off");
    }
    test = "g0";
    if (test == a) {
      digitalWrite(9, LOW);
      //     Serial.println("off");
    }




     //   Serial.println(a);

  }
}
