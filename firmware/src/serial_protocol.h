#pragma once

#include <Arduino.h>

class SerialProtocol {
public:
    static void init();
    static void process(); // Call in loop()
};
