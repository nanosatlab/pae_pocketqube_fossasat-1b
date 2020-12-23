#ifndef __SYNCBUFFER_H__
#define __SYNCBUFFER_H__

#include <cstring>
#include <mutex>
#include <vector>
#include <stdint.h>
#include <list>

#include "log.h"

#define BUFFER_DEFAULT_SIZE    1024

class SyncBuffer
{
public:
    SyncBuffer(uint32_t max_size = BUFFER_DEFAULT_SIZE);
    uint32_t available(void);
    uint32_t write(uint8_t* data, uint32_t data_size);
    uint32_t read(uint8_t* data, uint32_t data_size);
    uint32_t bytes(void);
    uint32_t get_next_item_size(void);
private:
    uint32_t max_size;
    uint32_t write_pos;
    uint32_t read_pos;
    std::vector<uint8_t> buffer;
    std::list<uint32_t> content_sizes;
    std::mutex locker;
    void update_pointer(uint32_t *pointer, uint32_t value);
    uint32_t do_bytes(void);
    uint32_t do_available(void);
};

#endif  /* __SYNCBUFFER_H__ */
