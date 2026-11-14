#include "display.h"
#include <SPI.h>

// 20 MHz stable SPI
static constexpr uint32_t LCD_SPI_HZ = 20000000;

static Arduino_HWSPI g_bus(PIN_LCD_DC, -1, &SPI, true);
// Pass PIN_LCD_RST (2) so Arduino_ST7789 manages hardware reset cleanly
static Arduino_ST7789 g_tft(&g_bus, PIN_LCD_RST, 0, true, SCREEN_W, SCREEN_H);

static uint8_t s_rotation = 0;

void Display::init() {
    // Backlight active LOW on GeekMagic
    pinMode((uint8_t)PIN_LCD_BL, OUTPUT);
    digitalWrite((uint8_t)PIN_LCD_BL, LOW);

    // Pure standard ST7789 initialization from official Arduino_GFX library
    g_tft.begin(LCD_SPI_HZ);
    g_tft.setRotation(s_rotation);
    g_tft.fillScreen(COLOR_BG_DARK);
}

Arduino_GFX* Display::getGfx() {
    return &g_tft;
}

void Display::setBacklight(bool on) {
    pinMode((uint8_t)PIN_LCD_BL, OUTPUT);
    digitalWrite((uint8_t)PIN_LCD_BL, on ? LOW : HIGH);
}

void Display::setRotation(uint8_t rot) {
    s_rotation = rot;
    g_tft.setRotation(s_rotation);
}

uint8_t Display::getRotation() {
    return s_rotation;
}
