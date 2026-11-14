#include "serial_protocol.h"
#include "avatar.h"
#include "hud.h"
#include "display.h"
#include <ArduinoJson.h>

static char s_rxBuffer[256];
static size_t s_rxIdx = 0;

void SerialProtocol::init() {
    Serial.begin(115200);
    s_rxIdx = 0;
}

void SerialProtocol::process() {
    while (Serial.available()) {
        char c = (char)Serial.read();
        if (c == '\n' || c == '\r') {
            if (s_rxIdx == 0) continue;
            s_rxBuffer[s_rxIdx] = '\0';
            s_rxIdx = 0;

            StaticJsonDocument<256> doc;
            DeserializationError err = deserializeJson(doc, s_rxBuffer);
            if (!err) {
                if (doc.containsKey("rot")) {
                    uint8_t rot = doc["rot"];
                    Display::setRotation(rot);
                    Hud::redrawAll();
                    AvatarEngine::init();
                }

                const char* act = doc["act"];
                const char* mood = doc["mood"];
                if (act) {
                    AvatarEngine::setActionByName(act, mood);
                    if (mood) Hud::updateMood(mood);
                } else if (mood) {
                    Hud::updateMood(mood);
                }

                bool hasQuotas = doc.containsKey("claude") || doc.containsKey("codex") || doc.containsKey("gemini");
                if (hasQuotas || doc.containsKey("msg")) {
                    int c = doc["claude"] | 95;
                    int x = doc["codex"] | 80;
                    int g = doc["gemini"] | 65;
                    const char* msg = doc["msg"] | nullptr;
                    Hud::setQuotas(c, x, g, msg);
                }

                Serial.println("{\"status\":\"ok\"}");
            } else {
                Serial.println("{\"status\":\"err\",\"reason\":\"json_parse_failed\"}");
            }
        } else {
            if (s_rxIdx < sizeof(s_rxBuffer) - 1) {
                s_rxBuffer[s_rxIdx++] = c;
            }
        }
    }
}
