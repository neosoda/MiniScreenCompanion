#include <Arduino.h>
#include "display.h"
#include "avatar.h"
#include "hud.h"
#include "serial_protocol.h"

void setup() {
    SerialProtocol::init();
    Serial.println("[Mini Screen Companion] Booting custom firmware...");

    Display::init();
    Hud::init();
    AvatarEngine::init();

    Serial.println("[Mini Screen Companion] Ready!");
}

void loop() {
    SerialProtocol::process();
    AvatarEngine::update();
    yield();
}
