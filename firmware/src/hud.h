#pragma once

#include <Arduino.h>

class Hud {
public:
    static void init();
    static void setQuotas(int claude, int codex, int gemini, const char* msg = nullptr);
    static void updateMood(const char* mood);
    static void redrawAll();

private:
    static void drawCardFrame();
    static void drawGauge(int16_t x, int16_t y, int16_t w, int16_t h, int pct, uint16_t color);
};
