#pragma once

#include <Arduino.h>

enum AvatarAction {
    ACT_IDLE = 0,
    ACT_WALK,
    ACT_DESK,
    ACT_COFFEE,
    ACT_SLEEP,
    ACT_PET
};

class AvatarEngine {
public:
    static void init();
    static void setAction(AvatarAction act, const char* label = nullptr);
    static void setActionByName(const char* name, const char* label = nullptr);
    static void update(); // Called in loop()
    static AvatarAction getCurrentAction();
    static const char* getCurrentLabel();

private:
    static void drawBackground();
    static void drawFrame(uint8_t frame);
    static void drawChibiFace(int16_t x, int16_t y, int8_t bob, bool blink, bool happy);
    static void drawLaptop(int16_t x, int16_t y);
    static void drawCoffeeCup(int16_t x, int16_t y, uint8_t steamFrame);
    static void drawSleepZ(int16_t x, int16_t y, uint8_t zFrame);
    static void drawHearts(int16_t x, int16_t y, uint8_t heartFrame);
};
