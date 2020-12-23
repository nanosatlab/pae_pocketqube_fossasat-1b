#ifndef __KISS_H__
#define __KISS_H__

#include "Arduino.h"
#include <list>
#include <stdint.h>
#include "log.h"

#define KISS_FEND    0xC0
#define KISS_FESC    0xDB
#define KISS_TFEND   0xDD
#define KISS_TFESC   0xDC

class Kiss
{
public:
    static bool write(const uint8_t *data, uint32_t data_size, bool debug = false);
    static uint32_t read(uint8_t *data, uint32_t data_size);
    static uint32_t available();
};

#endif  /* __KISS_H__ */
