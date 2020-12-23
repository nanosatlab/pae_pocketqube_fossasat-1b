#include "SyncBuffer.h"

SyncBuffer::SyncBuffer(uint32_t max_size)
    : max_size(max_size)
    , buffer(max_size)
{ }

uint32_t SyncBuffer::available(void)
{
    locker.lock();
    uint32_t tmp_available = do_available();
    locker.unlock();
    return tmp_available;
}

uint32_t SyncBuffer::do_available(void)
{
    return max_size - do_bytes();
}

uint32_t SyncBuffer::do_bytes(void)
{
    uint32_t tmp_length = write_pos - read_pos;
    if(tmp_length < 0) {
        /* Inverted ciruclar pointers */
        tmp_length = max_size - read_pos + write_pos;
    }
    return tmp_length;
}

uint32_t SyncBuffer::bytes(void)
{
    locker.lock();
    uint32_t tmp_length = do_bytes();
    locker.unlock();
    return tmp_length;
}

void SyncBuffer::update_pointer(uint32_t *pointer, uint32_t value)
{
    (*pointer) += value;
    (*pointer) %= max_size;
}

uint32_t SyncBuffer::write(uint8_t* data, uint32_t data_size)
{
    locker.lock();
    uint32_t tmp_size;
    if(do_available() > data_size) {
        if(write_pos + data_size < max_size) {
            memcpy(&buffer[write_pos], data, data_size);
            update_pointer(&write_pos, data_size);
        } else {
            uint32_t remaining = max_size - write_pos;
            memcpy(&buffer[write_pos], data, remaining);
            update_pointer(&write_pos, remaining);
            memcpy(&buffer[write_pos], &data[remaining], data_size - remaining);
            update_pointer(&write_pos, data_size - remaining);
        }
        tmp_size = data_size;
        content_sizes.push_back(data_size);
    }
    locker.unlock();
    return tmp_size;
}

uint32_t SyncBuffer::read(uint8_t* data, uint32_t data_size)
{
    locker.lock();
    uint32_t tmp_read;
    if(do_bytes() >= data_size)
    {
        if(read_pos + data_size < max_size) {
            memcpy(data, &buffer[read_pos], data_size);
            update_pointer(&read_pos, data_size);
        } else {
            uint32_t remaining = max_size - read_pos;
            memcpy(data, &buffer[read_pos], remaining);
            update_pointer(&read_pos, remaining);
            memcpy(&data[remaining], &buffer[read_pos], data_size - remaining);
            update_pointer(&read_pos, data_size - remaining);
        }
        tmp_read = data_size;
        content_sizes.pop_front();
    }
    locker.unlock();
    return tmp_read;
}

uint32_t SyncBuffer::get_next_item_size(void)
{
    locker.lock();
    uint32_t tmp_size = content_sizes.front();
    locker.unlock();
    return tmp_size;
}
