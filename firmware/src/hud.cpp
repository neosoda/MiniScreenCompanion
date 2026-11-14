#include "hud.h"
#include "display.h"

static int s_claude = 95;
static int s_codex  = 80;
static int s_gemini = 65;
static char s_msg[48] = "Systeme pret";
static char s_mood[32] = "Au calme";

static constexpr int16_t GAUGE_X = 16;
static constexpr int16_t GAUGE_W = 208;
static constexpr int16_t GAUGE_H = 6;

void Hud::drawGauge(int16_t x, int16_t y, int16_t w, int16_t h, int pct, uint16_t color) {
    Arduino_GFX* gfx = Display::getGfx();
    if (pct < 0) pct = 0;
    if (pct > 100) pct = 100;

    int16_t fillW = (w * pct) / 100;

    // Track background
    gfx->fillRoundRect(x, y, w, h, 2, 0x18E3);

    // Progress fill
    if (fillW > 0) {
        gfx->fillRoundRect(x, y, fillW, h, 2, color);
    }
}

void Hud::drawCardFrame() {
    Arduino_GFX* gfx = Display::getGfx();

    // Background fill for bottom 2/3
    gfx->fillRect(0, 80, SCREEN_W, SCREEN_H - 80, COLOR_BG_DARK);

    // Neon divider bar at y=80
    gfx->drawFastHLine(0, 80, SCREEN_W, COLOR_BORDER);
    gfx->drawFastHLine(20, 80, 200, 0x3CF7);

    // Header info at y=86
    gfx->setTextSize(1);
    gfx->setTextColor(0x7BEF, COLOR_BG_DARK);
    gfx->setCursor(16, 88);
    gfx->print("LIVE HUD");

    updateMood(s_mood);

    // Row 1: Claude
    gfx->setTextColor(COLOR_CLAUDE, COLOR_BG_DARK);
    gfx->setCursor(16, 104);
    gfx->print("CLAUDE");
    drawGauge(GAUGE_X, 118, GAUGE_W, GAUGE_H, s_claude, COLOR_CLAUDE);

    // Row 2: Codex
    gfx->setTextColor(COLOR_CODEX, COLOR_BG_DARK);
    gfx->setCursor(16, 138);
    gfx->print("CODEX");
    drawGauge(GAUGE_X, 152, GAUGE_W, GAUGE_H, s_codex, COLOR_CODEX);

    // Row 3: Gemini
    gfx->setTextColor(COLOR_GEMINI, COLOR_BG_DARK);
    gfx->setCursor(16, 172);
    gfx->print("GEMINI");
    drawGauge(GAUGE_X, 186, GAUGE_W, GAUGE_H, s_gemini, COLOR_GEMINI);

    // Values
    setQuotas(s_claude, s_codex, s_gemini, s_msg);
}

void Hud::init() {
    drawCardFrame();
}

void Hud::redrawAll() {
    drawCardFrame();
}

void Hud::updateMood(const char* mood) {
    if (mood) {
        strncpy(s_mood, mood, sizeof(s_mood) - 1);
        s_mood[sizeof(s_mood) - 1] = '\0';
    }
    Arduino_GFX* gfx = Display::getGfx();
    gfx->setTextSize(1);
    gfx->fillRect(110, 86, 115, 12, COLOR_BG_DARK);
    gfx->setTextColor(COLOR_TEXT_WHITE, COLOR_BG_DARK);

    int16_t len = strlen(s_mood);
    int16_t mx = 224 - (len * 6);
    if (mx < 110) mx = 110;
    gfx->setCursor(mx, 88);
    gfx->print(s_mood);
}

void Hud::setQuotas(int claude, int codex, int gemini, const char* msg) {
    Arduino_GFX* gfx = Display::getGfx();
    gfx->setTextSize(1);

    char buf[16];

    // Claude %
    s_claude = claude;
    snprintf(buf, sizeof(buf), "%3d%%", s_claude);
    gfx->fillRect(190, 104, 34, 10, COLOR_BG_DARK);
    gfx->setTextColor(COLOR_TEXT_WHITE, COLOR_BG_DARK);
    gfx->setCursor(190, 104);
    gfx->print(buf);
    drawGauge(GAUGE_X, 118, GAUGE_W, GAUGE_H, s_claude, COLOR_CLAUDE);

    // Codex %
    s_codex = codex;
    snprintf(buf, sizeof(buf), "%3d%%", s_codex);
    gfx->fillRect(190, 138, 34, 10, COLOR_BG_DARK);
    gfx->setTextColor(COLOR_TEXT_WHITE, COLOR_BG_DARK);
    gfx->setCursor(190, 138);
    gfx->print(buf);
    drawGauge(GAUGE_X, 152, GAUGE_W, GAUGE_H, s_codex, COLOR_CODEX);

    // Gemini %
    s_gemini = gemini;
    snprintf(buf, sizeof(buf), "%3d%%", s_gemini);
    gfx->fillRect(190, 172, 34, 10, COLOR_BG_DARK);
    gfx->setTextColor(COLOR_TEXT_WHITE, COLOR_BG_DARK);
    gfx->setCursor(190, 172);
    gfx->print(buf);
    drawGauge(GAUGE_X, 186, GAUGE_W, GAUGE_H, s_gemini, COLOR_GEMINI);

    // Footer status message
    if (msg) {
        strncpy(s_msg, msg, sizeof(s_msg) - 1);
        s_msg[sizeof(s_msg) - 1] = '\0';
    }

    // Status pill
    gfx->fillRoundRect(12, 208, 216, 20, 4, 0x10C6);
    gfx->drawRoundRect(12, 208, 216, 20, 4, COLOR_BORDER);

    // Status dot
    gfx->fillCircle(22, 218, 3, 0x05E5);

    // Status text
    gfx->setTextColor(COLOR_TEXT_WHITE, 0x10C6);
    gfx->setCursor(32, 215);
    gfx->print(s_msg);
}
