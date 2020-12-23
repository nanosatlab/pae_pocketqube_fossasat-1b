#include "log.h"

void LOG::info(const char *fmt, ...)
{
    va_list args;
    va_start(args, fmt);
    LOG::write("[INFO]", fmt, args);
    va_end(args);
}

void LOG::warn(const char *fmt, ...)
{
    va_list args;
    va_start(args, fmt);
    LOG::write("[WARN]", fmt, args);
    va_end(args);
}

void LOG::err(const char *fmt, ...)
{
    va_list args;
    va_start(args, fmt);
    LOG::write("[ERROR]", fmt, args);
    va_end(args);
}

void LOG::write(const char *type, const char *fmt, va_list args)
{
    std::ostringstream log_stream;
    char msg[LOG_MSG_LEN];
    vsnprintf(msg, LOG_MSG_LEN, fmt, args);
    log_stream << type << " " << msg << std::endl;
    std::string log_str = log_stream.str() + "\n";
    Kiss::write((uint8_t*)log_str.c_str(), log_str.length(), true);
}
