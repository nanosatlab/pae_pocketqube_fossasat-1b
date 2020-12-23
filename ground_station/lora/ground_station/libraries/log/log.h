#ifndef __LOG_H__
#define __LOG_H__

#include <sstream>
#include <string>
#include "Arduino.h"
#include "kiss.h"

#define LOG_MSG_LEN  1500

class LOG {
public:
    static void info(const char *msg, ...);
    static void warn(const char *msg, ...);
    static void err(const char *msg, ...);
private:
    static void write(const char *type, const char *fmt, va_list args);
};

#endif  /* __LOG_H__ */
