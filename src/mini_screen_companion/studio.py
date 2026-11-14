"""Companion Studio: a local-only, dependency-free browser preview and settings UI.

Never communicates with the screen or accepts remote network connections.
"""
import json
import logging
import webbrowser
from dataclasses import asdict, replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .collectors import get_dashboard_snapshot
from .core.config import AppConfig
from .renderers.cozy_avatar import render_cozy_avatar

logger = logging.getLogger(__name__)

SCENES = ("auto", "day", "night", "rain")
PALETTES = ("warm", "mint", "lavender")
ACTIONS = ("auto", "desk", "coffee", "pet", "run", "sleep")
METRICS = ("remaining", "used")

STUDIO_HTML = r"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Companion Studio · Living Companion V2</title>
<style>
:root{color-scheme:dark;font-family:Inter,"Segoe UI",Arial,sans-serif;
background:#080e1b;color:#e7edf8}*{box-sizing:border-box}
body{margin:0;min-height:100vh;background:radial-gradient(ellipse at 20% 4%,#21304f 0%,#080e1b 50%)}
header{max-width:1050px;margin:auto;padding:34px 24px 12px}
.eyebrow{font-size:11px;font-weight:800;color:#72dac9;letter-spacing:2px}
h1{font-size:clamp(26px,4vw,38px);letter-spacing:-1.4px;margin:8px 0}
.sub{color:#9cabc5;line-height:1.6;margin:0 0 10px}
main{display:grid;grid-template-columns:minmax(0,1fr) minmax(300px,370px);
gap:24px;max-width:1050px;padding:20px 24px 50px;margin:auto}
.panel{border-radius:20px;padding:25px;background:rgba(19,29,49,.91);
border:1px solid #33415a;box-shadow:0 16px 50px #050b1b66}
h2{font-size:17px;margin:0 0 16px}p{color:#91a2be;font-size:13px}
.preview{display:flex;align-items:center;justify-content:center;padding:28px 0;
background:radial-gradient(ellipse,#28344c,#11192a 74%);border-radius:14px}
#screen{width:240px;height:240px;image-rendering:pixelated;border-radius:10px;
box-shadow:0 18px 35px #010716dd,0 0 0 6px #34405a;display:block}
.hint{font-size:12px;color:#91a2be;line-height:1.6;padding-top:18px}
label{display:block;font-size:12px;font-weight:700;color:#ccd8ea;margin:16px 0 7px}
select,input[type=text],input[type=number]{width:100%;height:40px;border:1px solid #40526b;
border-radius:9px;background:#0b1425;color:#f3f8ff;padding:8px 10px;font:inherit}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:0 15px}
.check{display:flex;align-items:center;gap:9px;font-size:13px;margin-top:16px}
.check input{width:17px;height:17px;accent-color:#66dcc5}
.toolbar{display:flex;gap:10px;margin-top:25px;flex-wrap:wrap}
button,.download{border:0;text-decoration:none;border-radius:10px;padding:11px 16px;
font-size:13px;font-weight:800;cursor:pointer}
button{background:#6ce0ca;color:#081a1e}.download{background:#273b59;color:#e3eefa}
button:hover{background:#98efd9}.download:hover{background:#374b6a}
#status{min-height:20px;font-size:12px;color:#a9bdd7;margin-top:15px}
.badge{display:inline-block;background:#1c423e;border-radius:40px;color:#95f2d7;
padding:6px 11px;font-size:10px;letter-spacing:1px;font-weight:800}
footer{max-width:1050px;margin:0 auto;padding:0 24px 30px;
font-size:12px;color:#8294af}
@media(max-width:760px){main{grid-template-columns:1fr}.panel{padding:18px}}
</style></head><body>
<header><div class="eyebrow">TECHSENTINEL · MINI SCREEN COMPANION</div>
<h1>Living Companion Studio</h1>
<p class="sub">Façonne ton compagnon en pixel art, visualise les animations et sauvegarde
son univers. Aucun envoi vers l'écran depuis cet atelier.</p></header>
<main>
<section class="panel"><span class="badge">APERÇU LOCAL · 240 × 240</span>
<div class="preview" style="margin-top:18px"><img id="screen" alt="Prévisualisation animée" width="240" height="240"></div>
<div class="hint">La pièce occupe les 80 pixels supérieurs ; les quotas restent dans les 160 pixels
inférieurs. Le GIF animé est une prévisualisation sur PC : le firmware constructeur
ne reçoit pas ces animations.</div></section>
<section class="panel"><h2>Personnalisation</h2>
<label for="name">Nom du compagnon</label><input id="name" type="text" maxlength="16" placeholder="Neo">
<div class="grid">
<div><label for="action">Activité</label><select id="action">
<option value="auto">Automatique</option><option value="desk">Codage</option>
<option value="coffee">Café</option><option value="pet">Chat</option>
<option value="run">Marche</option><option value="sleep">Sommeil</option></select></div>
<div><label for="scene">Ambiance</label><select id="scene">
<option value="auto">Auto</option><option value="day">Jour</option>
<option value="night">Nuit</option><option value="rain">Pluie</option></select></div>
<div><label for="palette">Palette</label><select id="palette">
<option value="warm">Warm</option><option value="mint">Mint</option>
<option value="lavender">Lavender</option></select></div>
<div><label for="fps">Images / seconde</label><select id="fps">
<option value="4">4 FPS</option><option value="6">6 FPS</option>
<option value="8">8 FPS</option><option value="12">12 FPS</option></select></div>
</div>
<label class="check"><input type="checkbox" id="show_cat" checked>Afficher le chat</label>
<label class="check"><input type="checkbox" id="effects" checked>Microanimations et météo</label>
<label class="check"><input type="checkbox" id="demo">Quotas de démonstration (aperçu seulement)</label>
<div class="toolbar"><button id="save" type="button">Enregistrer le profil</button>
<a class="download" id="download" href="#" download="living-companion.gif">Exporter le GIF</a></div>
<div id="status" role="status" aria-live="polite"></div>
<p>Les paramètres enregistrés sont chargés au prochain démarrage du service.</p>
</section></main><footer>Companion Studio fonctionne uniquement sur 127.0.0.1.
Aucun flash, aucun upload matériel.</footer>
<script>
"use strict";
const ids=["name","action","scene","palette","fps","show_cat","effects","demo"];
const field=(id)=>document.getElementById(id);
const checkbox=(id)=>field(id).checked;
const settings=()=>({name:field("name").value,action:field("action").value,
scene:field("scene").value,palette:field("palette").value,
fps:Number(field("fps").value),show_cat:checkbox("show_cat"),
effects:checkbox("effects")});
let activeURL="";
function render(){
  const p=new URLSearchParams();
  const s=settings();
  Object.keys(s).forEach(k=>p.set(k,String(s[k])));
  p.set("demo",checkbox("demo")?"1":"0");
  p.set("t",String(Date.now()));
  activeURL="/api/preview?"+p.toString();
  field("screen").src=activeURL;
  field("download").href=activeURL;
}
field("screen").onerror=()=>field("status").textContent="Erreur de génération de l'aperçu.";
let delayed;
ids.forEach(id=>field(id).addEventListener("input",()=>{
  clearTimeout(delayed);delayed=setTimeout(render,130);
}));
async function init(){
  try{
    const r=await fetch("/api/config",{cache:"no-store"});
    if(!r.ok)throw new Error("Configuration inaccessible");
    const data=await r.json();
    const s=data.avatar;
    for(const id of ids){
      if(id==="demo")continue;
      if(id==="show_cat"||id==="effects")field(id).checked=s[id];
      else field(id).value=String(s[id]);
    }
    field("demo").checked=data.demo;
    render();
  }catch(e){field("status").textContent=e.message}
}
field("save").onclick=async()=>{
  field("status").textContent="Enregistrement...";
  try{
    const r=await fetch("/api/config",{method:"POST",
      headers:{"Content-Type":"application/json"},body:JSON.stringify(settings())});
    const data=await r.json();
    if(!r.ok)throw new Error(data.error||"Echec de la sauvegarde");
    field("status").textContent="Profil enregistré. Redémarre le service pour l'appliquer.";
  }catch(e){field("status").textContent=e.message}
};
init();
</script></body></html>
"""


def coerce_avatar(data, current):
    """Allowlist and validate every persisted setting, without path injection."""
    if not isinstance(data, dict):
        raise ValueError("Le profil doit etre un objet JSON.")
    invalid = set(data) - {"name", "action", "scene", "palette", "fps",
                           "show_cat", "effects"}
    if invalid:
        raise ValueError("Champs inconnus : " + ", ".join(sorted(invalid)))

    fields = {}
    for key, choices in (("action", ACTIONS), ("scene", SCENES),
                         ("palette", PALETTES)):
        value = data.get(key, getattr(current, key))
        if not isinstance(value, str) or value not in choices:
            raise ValueError("Valeur invalide : " + key)
        fields[key] = value

    name = data.get("name", current.name)
    if not isinstance(name, str) or len(name) > 16 or any(ord(ch) < 32 for ch in name):
        raise ValueError("Nom invalide (16 caracteres maximum).")
    fields["name"] = name

    fps = data.get("fps", current.fps)
    if type(fps) is not int or fps not in (4, 6, 8, 12):
        raise ValueError("FPS incorrect (4, 6, 8 ou 12).")
    fields["fps"] = fps

    for key in ("show_cat", "effects"):
        value = data.get(key, getattr(current, key))
        if type(value) is not bool:
            raise ValueError("Booleen attendu : " + key)
        fields[key] = value

    return replace(current, **fields)


def create_studio_server(config_path="config.json", port=8765, demo=False):
    """Create a loopback-only server. Port zero is supported for tests."""
    config_path = Path(config_path)
    cfg = AppConfig.load(str(config_path))

    class StudioHandler(BaseHTTPRequestHandler):
        def _send(self, status, body, mime):
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy",
                             "default-src 'self'; img-src 'self'; "
                             "style-src 'unsafe-inline'; script-src 'unsafe-inline'; "
                             "connect-src 'self'; object-src 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, status, payload):
            self._send(status, json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                       "application/json; charset=utf-8")

        def _same_host(self):
            return self.headers.get("Host", "") == "127.0.0.1:" + str(self.server.server_port)

        def do_GET(self):
            if not self._same_host():
                return self._json(403, {"error": "Local access only"})
            url = urlsplit(self.path)
            if url.path == "/":
                return self._send(200, STUDIO_HTML.encode("utf-8"),
                                  "text/html; charset=utf-8")
            if url.path == "/api/config":
                return self._json(200, {"avatar": asdict(cfg.avatar), "demo": demo})
            if url.path == "/api/preview":
                query = parse_qs(url.query)
                try:
                    choices = {}
                    for key in ("name", "scene", "palette", "action"):
                        if key in query:
                            choices[key] = query[key][-1]
                    if "fps" in query:
                        choices["fps"] = int(query["fps"][-1])
                    for key in ("show_cat", "effects"):
                        if key in query:
                            value = query[key][-1]
                            if value not in ("true", "false"):
                                raise ValueError("Booleen incorrect")
                            choices[key] = value == "true"
                    avatar = coerce_avatar(choices, cfg.avatar)
                    request_demo = query.get("demo", ["1" if demo else "0"])[-1] == "1"
                    snapshot = get_dashboard_snapshot(cfg, use_mock=request_demo)
                    data = render_cozy_avatar(snapshot, avatar_cfg=avatar, animated=True)
                except (ValueError, TypeError) as exc:
                    return self._json(400, {"error": str(exc)})
                except Exception:
                    logger.exception("Studio preview failed")
                    return self._json(500, {"error": "Generation impossible"})
                return self._send(200, data, "image/gif")
            return self._json(404, {"error": "Not found"})

        def do_POST(self):
            if not self._same_host():
                return self._json(403, {"error": "Local access only"})
            origin = self.headers.get("Origin")
            expected_origin = "http://127.0.0.1:" + str(self.server.server_port)
            if origin is not None and origin != expected_origin:
                return self._json(403, {"error": "Origin refused"})
            site = self.headers.get("Sec-Fetch-Site")
            if site is not None and site not in ("same-origin", "none"):
                return self._json(403, {"error": "Cross-site request refused"})
            if urlsplit(self.path).path != "/api/config":
                return self._json(404, {"error": "Not found"})
            if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
                return self._json(415, {"error": "JSON required"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 4096:
                    raise ValueError("Invalid payload size")
                data = json.loads(self.rfile.read(length).decode("utf-8"))
                next_avatar = coerce_avatar(data, cfg.avatar)
                previous = cfg.avatar
                cfg.avatar = next_avatar
                try:
                    cfg.save(str(config_path))
                except OSError:
                    cfg.avatar = previous
                    raise
                return self._json(200, {"saved": True})
            except (ValueError, TypeError, UnicodeError) as exc:
                return self._json(400, {"error": str(exc)})
            except OSError:
                logger.exception("Could not save Studio configuration")
                return self._json(500, {"error": "Impossible d'enregistrer"})

        def log_message(self, format, *args):
            logger.info("Studio: " + format, *args)

    server = ThreadingHTTPServer(("127.0.0.1", port), StudioHandler)
    server.daemon_threads = True
    return server


def serve_studio(config_path="config.json", port=8765, open_browser=True, demo=False):
    server = create_studio_server(config_path, port=port, demo=demo)
    url = "http://127.0.0.1:" + str(server.server_port) + "/"
    print("Companion Studio: " + url + " (LOCAL ONLY, no screen uploads)")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
