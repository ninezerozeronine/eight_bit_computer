#include <Arduino.h>

#include "button.h"
#include "rom_0.h"

#define ROM_SEL_BUTTON_PIN 1
#define MODE_SEL_BUTTON_PIN 2
#define GO_BUTTON_PIN 3
#define _CE_PIN 4
#define _OE_PIN 5
#define _WE_PIN 6
#define NUM_DATA_PINS 8
#define NUM_ADDRESS_PINS 15

const int DATA_PINS[NUM_DATA_PINS] = {1,2,3,4,5,6,7,8};
const int ADDRESS_PINS[NUM_ADDRESS_PINS] = {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
const byte* ROMS[] = {ROM_0};

Button rom_sel_button(ROM_SEL_BUTTON_PIN);
Button mode_sel_button(MODE_SEL_BUTTON_PIN);
Button go_button(GO_BUTTON_PIN);

int selected_rom = 0;
int mode = 0;

void setup() {
    // Called once at Arduino startup.
    digitalWrite(_CE_PIN, HIGH);
    pinMode(_CE_PIN, OUTPUT);
    
    digitalWrite(_OE_PIN, HIGH);
    pinMode(_OE_PIN, OUTPUT);
    digitalWrite(_WE_PIN, HIGH);
    pinMode(_WE_PIN, OUTPUT);

    digitalWrite(_CE_PIN, LOW);

    set_datapins_mode(INPUT)

    // Set all the address pint to output and low
    for (int index = 0; index <= NUM_ADDRESS_PINS; index++) {
        digitalWrite(ADDRESS_PINS[index], LOW);
        pinMode(ADDRESS_PINS[index], OUTPUT);
        
    }

    rom_sel_button.init();
    mode_sel_button.init();
    go_button.init();

    Serial.begin(9600);
    // wait for serial port to connect. Needed for native USB port only
    while (!Serial) {
    ; 
    }
}

void loop() {
    // Main loop function for arduino.
    rom_sel_button.update(&rom_sel_button_pressed, NULL);
    mode_sel_button.update(&mode_sel_button_pressed, NULL);
    go_button.update(&go_button_pressed, NULL);
}

void set_datapins_mode(int mode) {
    // Set the mode of the data pins
    //
    // Args:
    //     mode: The mode to set the pins to. E.g. INPUT, INPUT_PULLUP or OUTPUT.
    for (int index = 0; index <= NUM_DATA_PINS, index++) {
        pinMode(DATA_PINS[index], mode);
    }
}

void set_datapins_value(byte value){
    // Set the datapins to represent a value in binary.
    //
    // Args:
    //     value: The value to set the data pins to.
    for (int index = 0; index <= NUM_DATA_PINS, index++) {
        digitalWrite(DATA_PINS[index], value & 1);
        value = value >> 1;
    }
}

void set_addresspins_value(unsigned int address) {
    // Set an address on the address pins
    //
    // Args:
    //     address: The value to set the address pins to.
    for (int index = 0; index <= NUM_ADDRESS_PINS, index++) {
        digitalWrite(ADDRESS_PINS[index], address & 1);
        address = address >> 1;
    }
}

void write_eeprom_data(byte data[]) {
    set_datapins_mode(OUTPUT);

    num_addresses = sizeof(data);
    for (unsigned int address = 0; address < num_addresses; address++) {
        set_addresspins_value(address);
        delayMicroseconds(3);
        byte value = pgm_read_byte_near(data + address);
        set_datapins_value(value);

        digitalWrite(_WE_PIN, LOW);
        delayMicroseconds(3);
        digitalWrite(_WE_PIN, HIGH);
        delayMicroseconds(3);
    }

    set_datapins_value(0);
    set_datapins_mode(INPUT);
}

byte read_current_byte(){
    // Read the currently addressed byte.
    //
    // Expects:
    // * The address to already be set
    // * Time given for the address to settle
    // * The data pins to be in input mode

    byte current_byte = 0;
    for (int index = 0; index <= NUM_DATA_PINS, index ++) {
        current_byte = (current_byte << 1) + digitalRead(DATA_PINS[index]);
    }
    return byte
}

void read_eeprom_data() {
    digitalWrite(_OE_PIN, HIGH);
    set_datapins_mode(INPUT)

    delayMicroseconds(3);
    for (unsigned int base = 0; base < pow(2,15); base+=16) {
        byte byte_row[16];
        for (unsigned int offset = 0; offset <= 15; offset += 1) {
            set_addresspins_value(base + offset);
            delayMicroseconds(3);
            byte_row[offset] = read_current_byte()
        char buf[80];
        sprintf(buf, "%03x:  %02x %02x %02x %02x  %02x %02x %02x %02x    %02x %02x %02x %02x  %02x %02x %02x %02x",
                base,
                byte_row[0], byte_row[1], byte_row[2], byte_row[3], byte_row[4], byte_row[5], byte_row[6], byte_row[7],
                byte_row[8], byte_row[9], byte_row[10], byte_row[11], byte_row[12], byte_row[13], byte_row[14], byte_row[15]);
        Serial.println(buf);

    digitalWrite(_OE_PIN, LOW);
}

void rom_sel_button_pressed(){
    
}

void mode_sel_button_pressed(){
    
}

void go_button_pressed(){
    
}