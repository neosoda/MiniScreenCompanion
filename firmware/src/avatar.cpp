#include "avatar.h"
#include "display.h"

// Pixel palette (RGB565)
static constexpr uint16_t C_SKIN      = 0xFEF9; // #fcdeca
static constexpr uint16_t C_BLUSH     = 0xFD55; // #fcafaf
static constexpr uint16_t C_HAIR      = 0x59C4; // #5c3a24
static constexpr uint16_t C_HAIR_HL   = 0x82AA; // #825537
static constexpr uint16_t C_EYE       = 0x18C3; // #18181c
static constexpr uint16_t C_WHITE     = 0xFFFF; // #ffffff (White hoodie)
static constexpr uint16_t C_HOOD_SHD  = 0xCE79; // #cbd5e1 (Shadow)
static constexpr uint16_t C_PANTS     = 0x2965; // #2d3748 slate
static constexpr uint16_t C_WALL_DAY  = 0xF77A; // #f5eee2 warm cream
static constexpr uint16_t C_WALL_NITE = 0x1967; // #1e293b dark slate
static constexpr uint16_t C_FLOOR     = 0x8AA3; // #8c531b wood floor
static constexpr uint16_t C_WINDOW_BG = 0x3CF7; // #38bdf8 sky blue
static constexpr uint16_t C_WINDOW_NT = 0x08A6; // #0f172a night sky
static constexpr uint16_t C_FRAME_WD  = 0x51A1; // #59391d wood frame
static constexpr uint16_t C_CYAN      = 0x3CF7; // #38bdf8 screen glow
static constexpr uint16_t C_HEART     = 0xF94B; // #f43f5e pink heart
static constexpr uint16_t C_GOLD      = 0xFEE8; // #fde047 stars/moon

static AvatarAction s_action = ACT_IDLE;
static char s_label[32] = "Au calme";
static uint32_t s_lastFrameTime = 0;
static uint8_t s_frameIndex = 0;
static bool s_needsFullRedraw = true;

static int16_t s_avatarX = 110;
static int16_t s_avatarY = 32;
static int8_t s_walkDir = 1;

void AvatarEngine::init() {
    s_needsFullRedraw = true;
    s_lastFrameTime = millis();
}

void AvatarEngine::setAction(AvatarAction act, const char* label) {
    if (s_action != act) {
        s_action = act;
        s_frameIndex = 0;
        s_needsFullRedraw = true;
    }
    if (label && strlen(label) > 0) {
        strncpy(s_label, label, sizeof(s_label) - 1);
        s_label[sizeof(s_label) - 1] = '\0';
    }
}

void AvatarEngine::setActionByName(const char* name, const char* label) {
    if (!name) return;
    if (strcmp(name, "idle") == 0) setAction(ACT_IDLE, label ? label : "Au calme");
    else if (strcmp(name, "walk") == 0 || strcmp(name, "run") == 0) setAction(ACT_WALK, label ? label : "En balade");
    else if (strcmp(name, "desk") == 0 || strcmp(name, "type") == 0) setAction(ACT_DESK, label ? label : "En plein code");
    else if (strcmp(name, "coffee") == 0) setAction(ACT_COFFEE, label ? label : "Pause cafe");
    else if (strcmp(name, "sleep") == 0) setAction(ACT_SLEEP, label ? label : "Mode veille Zzz");
    else if (strcmp(name, "pet") == 0) setAction(ACT_PET, label ? label : "Calin chat");
}

AvatarAction AvatarEngine::getCurrentAction() {
    return s_action;
}

const char* AvatarEngine::getCurrentLabel() {
    return s_label;
}

void AvatarEngine::drawBackground() {
    Arduino_GFX* gfx = Display::getGfx();
    bool isNight = (s_action == ACT_SLEEP);
    uint16_t c_wall = isNight ? C_WALL_NITE : C_WALL_DAY;

    // Wall (y: 0..55)
    gfx->fillRect(0, 0, 240, 56, c_wall);

    // Floor (y: 56..79)
    gfx->fillRect(0, 56, 240, 24, C_FLOOR);
    gfx->drawFastHLine(0, 56, 240, 0x6201);
    gfx->drawFastHLine(0, 68, 240, 0x7261);

    // Window (x: 180..215, y: 8..38)
    uint16_t c_win = isNight ? C_WINDOW_NT : C_WINDOW_BG;
    gfx->fillRect(180, 8, 36, 30, c_win);
    gfx->drawRect(180, 8, 36, 30, C_FRAME_WD);
    gfx->drawFastVLine(198, 8, 30, C_FRAME_WD);
    gfx->drawFastHLine(180, 23, 36, C_FRAME_WD);

    if (isNight) {
        gfx->fillCircle(190, 16, 5, C_GOLD);
        gfx->fillCircle(192, 15, 4, C_WINDOW_NT);
        gfx->drawPixel(205, 13, C_GOLD);
        gfx->drawPixel(208, 28, C_GOLD);
        gfx->drawPixel(185, 30, C_GOLD);
    } else {
        gfx->fillCircle(188, 15, 4, C_GOLD);
    }

    // Mini plant
    gfx->fillRect(18, 46, 12, 10, 0xB343);
    gfx->fillCircle(24, 40, 7, 0x24C5);
    gfx->fillCircle(20, 42, 5, 0x3568);
}

void AvatarEngine::drawChibiFace(int16_t x, int16_t y, int8_t bob, bool blink, bool happy) {
    Arduino_GFX* gfx = Display::getGfx();
    int16_t fy = y - bob;

    gfx->fillRoundRect(x + 2, fy + 3, 13, 11, 3, C_SKIN);
    gfx->drawPixel(x + 3, fy + 9, C_BLUSH);
    gfx->drawPixel(x + 13, fy + 9, C_BLUSH);
    gfx->drawPixel(x + 8, fy + 10, 0xBA69);

    if (blink || s_action == ACT_SLEEP) {
        gfx->drawFastHLine(x + 5, fy + 7, 3, C_EYE);
        gfx->drawFastHLine(x + 10, fy + 7, 3, C_EYE);
    } else if (happy) {
        gfx->drawPixel(x + 5, fy + 7, C_EYE);
        gfx->drawPixel(x + 6, fy + 6, C_EYE);
        gfx->drawPixel(x + 7, fy + 7, C_EYE);
        gfx->drawPixel(x + 10, fy + 7, C_EYE);
        gfx->drawPixel(x + 11, fy + 6, C_EYE);
        gfx->drawPixel(x + 12, fy + 7, C_EYE);
    } else {
        gfx->fillRect(x + 5, fy + 6, 2, 3, C_EYE);
        gfx->drawPixel(x + 5, fy + 6, C_WHITE);
        gfx->fillRect(x + 10, fy + 6, 2, 3, C_EYE);
        gfx->drawPixel(x + 10, fy + 6, C_WHITE);
    }

    gfx->fillRoundRect(x + 1, fy, 15, 6, 2, C_HAIR);
    gfx->fillCircle(x + 2, fy + 5, 4, C_HAIR);
    gfx->fillCircle(x + 14, fy + 5, 4, C_HAIR);
    gfx->drawPixel(x + 5, fy + 1, C_HAIR_HL);
    gfx->drawPixel(x + 6, fy + 1, C_HAIR_HL);
    gfx->drawPixel(x + 9, fy + 1, C_HAIR_HL);
}

void AvatarEngine::drawLaptop(int16_t x, int16_t y) {
    Arduino_GFX* gfx = Display::getGfx();
    gfx->fillRect(x - 6, y + 16, 36, 4, 0x9B84);
    gfx->fillRect(x - 4, y + 20, 4, 12, 0x7242);
    gfx->fillRect(x + 24, y + 20, 4, 12, 0x7242);

    gfx->fillRect(x + 2, y + 5, 14, 11, 0x3186);
    gfx->fillRect(x + 3, y + 6, 12, 9, C_CYAN);
    gfx->fillRect(x, y + 15, 18, 2, 0x4A69);
}

void AvatarEngine::drawCoffeeCup(int16_t x, int16_t y, uint8_t steamFrame) {
    Arduino_GFX* gfx = Display::getGfx();
    gfx->fillRect(x, y + 8, 8, 9, C_WHITE);
    gfx->drawFastHLine(x + 8, y + 10, 3, C_WHITE);
    gfx->drawFastVLine(x + 10, y + 10, 4, C_WHITE);
    gfx->drawFastHLine(x + 8, y + 13, 3, C_WHITE);

    int8_t sOff = (steamFrame % 2 == 0) ? 0 : 1;
    gfx->drawPixel(x + 2 + sOff, y + 5, 0xC618);
    gfx->drawPixel(x + 3 - sOff, y + 3, 0xD67A);
    gfx->drawPixel(x + 5 + sOff, y + 4, 0xC618);
}

void AvatarEngine::drawSleepZ(int16_t x, int16_t y, uint8_t zFrame) {
    Arduino_GFX* gfx = Display::getGfx();
    int16_t zY = y - (zFrame * 3);
    int16_t zX = x + (zFrame * 4);

    gfx->setTextSize(1);
    gfx->setTextColor(0x7D3C, s_action == ACT_SLEEP ? C_WALL_NITE : C_WALL_DAY);
    gfx->setCursor(zX, zY);
    gfx->print("Z");
    if (zFrame > 1) {
        gfx->setCursor(zX + 6, zY - 5);
        gfx->print("z");
    }
}

void AvatarEngine::drawHearts(int16_t x, int16_t y, uint8_t heartFrame) {
    Arduino_GFX* gfx = Display::getGfx();
    int16_t hY = y - 4 - (heartFrame * 2);
    int16_t hX = x + ((heartFrame % 2 == 0) ? -6 : 14);

    gfx->fillRect(hX + 1, hY, 2, 2, C_HEART);
    gfx->fillRect(hX + 4, hY, 2, 2, C_HEART);
    gfx->fillRect(hX, hY + 2, 7, 2, C_HEART);
    gfx->fillRect(hX + 1, hY + 4, 5, 2, C_HEART);
    gfx->fillRect(hX + 2, hY + 6, 3, 2, C_HEART);
}

void AvatarEngine::drawFrame(uint8_t frame) {
    Arduino_GFX* gfx = Display::getGfx();

    bool isNight = (s_action == ACT_SLEEP);
    uint16_t c_wall = isNight ? C_WALL_NITE : C_WALL_DAY;
    gfx->fillRect(35, 20, 140, 36, c_wall);
    gfx->fillRect(35, 56, 140, 22, C_FLOOR);
    gfx->drawFastHLine(35, 56, 140, 0x6201);
    gfx->drawFastHLine(35, 68, 140, 0x7261);

    int16_t ax = s_avatarX;
    int16_t ay = s_avatarY;
    int8_t bob = (frame % 2 == 0) ? 0 : 1;
    bool blink = (frame == 3);

    switch (s_action) {
        case ACT_IDLE: {
            gfx->fillRoundRect(ax + 1, ay + 14 - bob, 15, 13, 3, C_WHITE);
            gfx->drawFastHLine(ax + 3, ay + 20 - bob, 11, C_HOOD_SHD);
            gfx->fillRect(ax + 3, ay + 26, 4, 6, C_PANTS);
            gfx->fillRect(ax + 10, ay + 26, 4, 6, C_PANTS);
            gfx->fillRect(ax + 2, ay + 31, 5, 2, C_WHITE);
            gfx->fillRect(ax + 10, ay + 31, 5, 2, C_WHITE);

            drawChibiFace(ax, ay, bob, blink, false);
            break;
        }

        case ACT_WALK: {
            s_avatarX += (s_walkDir * 2);
            if (s_avatarX > 140) { s_walkDir = -1; }
            if (s_avatarX < 70)  { s_walkDir = 1;  }
            ax = s_avatarX;

            int8_t legL = (frame % 2 == 0) ? 2 : -2;
            int8_t legR = -legL;

            gfx->fillRoundRect(ax + 1, ay + 14 - bob, 15, 13, 3, C_WHITE);
            gfx->fillRect(ax + 3, ay + 26 + legL, 4, 5, C_PANTS);
            gfx->fillRect(ax + 10, ay + 26 + legR, 4, 5, C_PANTS);

            drawChibiFace(ax, ay, bob, false, false);
            break;
        }

        case ACT_DESK: {
            gfx->fillRect(ax + 2, ay + 25, 13, 4, 0x7242);
            gfx->drawFastVLine(ax + 8, ay + 29, 6, 0x51A1);

            gfx->fillRoundRect(ax + 1, ay + 14 - bob, 15, 12, 3, C_WHITE);
            gfx->fillRect(ax + 14, ay + 19 - bob, 6, 3, C_WHITE);

            drawChibiFace(ax, ay, bob, blink, false);
            drawLaptop(ax + 16, ay + 6);
            break;
        }

        case ACT_COFFEE: {
            gfx->fillRoundRect(ax + 1, ay + 14 - bob, 15, 13, 3, C_WHITE);
            gfx->fillRect(ax + 3, ay + 26, 4, 6, C_PANTS);
            gfx->fillRect(ax + 10, ay + 26, 4, 6, C_PANTS);

            gfx->fillRect(ax + 13, ay + 17 - bob, 4, 3, C_WHITE);
            drawCoffeeCup(ax + 16, ay + 11 - bob, frame);

            drawChibiFace(ax, ay, bob, false, true);
            break;
        }

        case ACT_SLEEP: {
            gfx->fillRoundRect(ax - 2, ay + 24, 22, 9, 3, 0x4296);
            gfx->fillRoundRect(ax, ay + 16, 18, 10, 3, C_WHITE);
            drawChibiFace(ax, ay + 4, 0, true, false);
            drawSleepZ(ax + 16, ay + 12, frame);
            break;
        }

        case ACT_PET: {
            gfx->fillRoundRect(ax + 1, ay + 14 - bob, 15, 13, 3, C_WHITE);
            gfx->fillRect(ax + 3, ay + 26, 4, 6, C_PANTS);
            gfx->fillRect(ax + 10, ay + 26, 4, 6, C_PANTS);

            gfx->fillRect(ax + 14, ay + 19 - bob, 6, 3, C_WHITE);

            int16_t cx = ax + 18;
            int16_t cy = ay + 22;
            gfx->fillRoundRect(cx, cy + 3, 10, 8, 2, 0xFA80);
            gfx->fillCircle(cx + 8, cy + 3, 3, 0xFA80);
            gfx->drawPixel(cx + 7, cy, 0xFA80);
            gfx->drawPixel(cx + 9, cy, 0xFA80);
            gfx->drawPixel(cx + 9, cy + 3, C_EYE);

            drawChibiFace(ax, ay, bob, false, true);
            drawHearts(ax + 10, ay + 2, frame);
            break;
        }
    }
}

void AvatarEngine::update() {
    uint32_t now = millis();
    if (now - s_lastFrameTime < 66) {
        return;
    }
    s_lastFrameTime = now;

    if (s_needsFullRedraw) {
        drawBackground();
        s_needsFullRedraw = false;
    }

    s_frameIndex = (s_frameIndex + 1) % 4;
    drawFrame(s_frameIndex);
}
