#include "kiss.h"

bool Kiss::write(const uint8_t *data, uint32_t data_size, bool debug)
{
    std::list<uint8_t> frame;
    uint8_t b;
    /* Include two FEND */
    frame.push_back(KISS_FEND);
    /* Include content */
    for(unsigned int i = 0; i < data_size; i++) {
        b = data[i];
        if(b == KISS_FEND) {
            frame.push_back(KISS_FESC);
            frame.push_back(KISS_TFEND);
        } else if(b == KISS_FESC) {
            frame.push_back(KISS_FESC);
            frame.push_back(KISS_TFESC);
        } else {
            frame.push_back(b);
        }
    }
    /* Close the frame with FEND */
    frame.push_back(KISS_FEND);
    /* Send through the UART */
    uint8_t chunk[frame.size()];
    std::copy(frame.begin(), frame.end(), chunk);
    size_t written = Serial.write(chunk, frame.size());
    if(written != frame.size()) {
        if(debug == false) {
            LOG::err("Transmitted different amount of chars: %d != %d", written, frame.size());
        }
        return false;
    }
    return true;
}

uint32_t Kiss::read(uint8_t *data, uint32_t data_size)
{
    uint8_t b;
    bool started_frame = false;
    bool finished_frame = false;
    bool fesc_found = false;
    std::list<uint8_t> frame;
    double start_time;

    if(Serial.available() > 0) {
        start_time = millis();
        while(finished_frame == false) {
            if(Serial.available() > 0) {
                b = (uint8_t)Serial.read();
                /* There is data to process */
                if((b & 0xFF) == KISS_FEND && started_frame == false) {
                    started_frame = true;
                } else if((b & 0xFF) == KISS_FEND && finished_frame == false) {
                    finished_frame = true;
                } else if((b & 0xFF) == KISS_FESC && fesc_found == false) {
                    fesc_found = true;
                } else if((b & 0xFF) == KISS_TFEND && fesc_found == true) {
                    frame.push_back(KISS_FEND);
                    fesc_found = false;
                } else if((b & 0xFF) == KISS_TFESC && fesc_found == true) {
                    frame.push_back(KISS_FESC);
                    fesc_found = false;
                } else if(started_frame == true){
                    frame.push_back(b);
                }
                if(started_frame == true && finished_frame == false) {
                    start_time = millis();
                }
            } else if(millis() >= start_time + 10) {    // waiting 10 ms to receive a byte
                //LOG::warn("Started KISS frame, but no char received; cleanning frame.");
                return 0;
            }
        }
        std::copy(frame.begin(), frame.end(), data);
    }
    return frame.size();
}

uint32_t Kiss::available()
{
    return Serial.available();
}

