#pragma once

#include <Arduino.h>
#include <Arduino_GFX_Library.h>

static constexpr int16_t SCREEN_W = 240;
static constexpr int16_t SCREEN_H = 240;
static constexpr int16_t AVATAR_H = 80;

// Pinout GeekMagic
static constexpr int8_t PIN_LCD_DC  = 0;
static constexpr int8_t PIN_LCD_RST = 2;
static constexpr int8_t PIN_LCD_BL  = 5;

// RGB565 Colors
static constexpr uint16_t COLOR_BG_DARK    = 0x0863; // #0a0e1a dark slate
static constexpr uint16_t COLOR_CARD_BG    = 0x10C6; // #131a29 card background
static constexpr uint16_t COLOR_BORDER     = 0x216A; // #212c44 card border
static constexpr uint16_t COLOR_TEXT_WHITE = 0xFFFF; // #ffffff
static constexpr uint16_t COLOR_TEXT_MUTED = 0x8410; // #808080
static constexpr uint16_t COLOR_CLAUDE     = 0xD380; // #d97706 warm amber / coral
static constexpr uint16_t COLOR_CODEX      = 0x05E5; // #10b981 emerald green
static constexpr uint16_t COLOR_GEMINI     = 0x3C1F; // #3b82f6 royal blue
static constexpr uint16_t COLOR_WARN       = 0xFBE0; // #f59e0b yellow warning
static constexpr uint16_t COLOR_CRIT       = 0xF904; // #ef4444 red alert

class Display {
public:
    static void init();
    static Arduino_GFX* getGfx();
    static void setBacklight(bool on);
    static void setRotation(uint8_t rot);
    static uint8_t getRotation();
};
