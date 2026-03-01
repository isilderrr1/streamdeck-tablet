from flask import Flask, jsonify, send_from_directory
import subprocess
import requests
import time
from icalendar import Calendar
from dateutil.rrule import rrulestr
from datetime import datetime, timedelta, timezone

app = Flask(__name__, static_folder="static")

# ====== CONFIG ======

# Google Calendar ICS "indirizzo segreto"
GOOGLE_ICS_URL = ""

# Cache calendario
ICS_CACHE_SECONDS = 60
_ics_cache = {"ts": 0.0, "events": []}

# AutoHotkey v2
AHK = r"C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
AHK_SCRIPT = r"C:\StreamDeckTablet\macros\windows_macros.ahk"

MACROS = {
    "terminal_main": [AHK, AHK_SCRIPT, "terminal_main"],
    "vscode_mon2":   [AHK, AHK_SCRIPT, "vscode_mon2"],
    "youtube_mon3":  [AHK, AHK_SCRIPT, "youtube_mon3"],
    "discord_mon2":  [AHK, AHK_SCRIPT, "discord_mon2"],
    # aggiungi qui altre macro quando vuoi
}

# Meteo (Open-Meteo, senza API key)
WEATHER_LAT = 40.8518   # Roma (cambia se vuoi)
WEATHER_LON = 14.2681
WEATHER_TTL_SECONDS = 10 * 60  # 10 minuti
_weather_cache = {"ts": 0.0, "data": None}


# ====== ROUTES: UI / STATIC ======

@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/static/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

# ====== HEALTH (per modalità offline sul tablet) ======

@app.get("/api/health")
def api_health():
    return jsonify({"ok": True})



# ====== ROUTES: MACROS ======

@app.post("/api/run/<name>")
def run_macro(name: str):
    if name not in MACROS:
        return jsonify({"ok": False, "error": "Macro not found"}), 404
    try:
        subprocess.Popen(
            MACROS[name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False
        )
        return jsonify({"ok": True, "macro": name})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ====== GOOGLE CALENDAR (ICS) ======

def _expand_rrule(component, window_start, window_end):
    dtstart = component.get("dtstart").dt
    dtend_prop = component.get("dtend")

    if dtend_prop:
        dtend = dtend_prop.dt
        duration = (dtend - dtstart) if isinstance(dtstart, datetime) and isinstance(dtend, datetime) else timedelta(days=1)
    else:
        duration = timedelta(hours=1) if isinstance(dtstart, datetime) else timedelta(days=1)

    rrule_obj = component.get("rrule")
    parts = []
    for k, v in rrule_obj.items():
        if isinstance(v, list):
            v = ",".join(str(x) for x in v)
        parts.append(f"{k}={v}")
    rrule_str = "RRULE:" + ";".join(parts)

    base = dtstart if isinstance(dtstart, datetime) else datetime(dtstart.year, dtstart.month, dtstart.day, tzinfo=timezone.utc)
    rule = rrulestr(rrule_str, dtstart=base)

    occ = []
    for o in rule.between(window_start, window_end, inc=True):
        occ.append((o, o + duration))
    return occ


def fetch_events():
    now = time.time()
    if now - _ics_cache["ts"] < ICS_CACHE_SECONDS:
        return _ics_cache["events"]

    if not GOOGLE_ICS_URL or "INCOLLA_QUI" in GOOGLE_ICS_URL:
        _ics_cache["ts"] = now
        _ics_cache["events"] = []
        return []

    window_start = datetime.now(timezone.utc) - timedelta(days=7)
    window_end = datetime.now(timezone.utc) + timedelta(days=30)

    r = requests.get(GOOGLE_ICS_URL, timeout=10)
    r.raise_for_status()

    cal = Calendar.from_ical(r.text)
    events = []

    for c in cal.walk():
        if c.name != "VEVENT":
            continue

        uid = str(c.get("uid", ""))
        title = str(c.get("summary", ""))
        location = str(c.get("location", ""))

        dtstart = c.get("dtstart").dt
        dtend_prop = c.get("dtend")
        dtend = dtend_prop.dt if dtend_prop else None

        # Ricorrenze
        if c.get("rrule"):
            for idx, (s, e) in enumerate(_expand_rrule(c, window_start, window_end)):
                events.append({
                    "id": f"{uid}__{idx}",
                    "title": title,
                    "start": s.isoformat(),
                    "end": e.isoformat(),
                    "extendedProps": {"location": location},
                })
            continue

        # All-day (date)
        if not isinstance(dtstart, datetime):
            events.append({
                "id": uid,
                "title": title,
                "start": dtstart.isoformat(),
                "allDay": True,
                "extendedProps": {"location": location},
            })
            continue

        s = dtstart if dtstart.tzinfo else dtstart.replace(tzinfo=timezone.utc)
        e = (dtend if dtend else (s + timedelta(hours=1)))
        e = e if e.tzinfo else e.replace(tzinfo=timezone.utc)

        if e < window_start or s > window_end:
            continue

        events.append({
            "id": uid,
            "title": title,
            "start": s.isoformat(),
            "end": e.isoformat(),
            "extendedProps": {"location": location},
        })

    _ics_cache["ts"] = now
    _ics_cache["events"] = events
    return events


@app.get("/api/events")
def api_events():
    try:
        return jsonify(fetch_events())
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ====== WEATHER (Open-Meteo) ======

@app.get("/api/weather")
def api_weather():
    now = time.time()

    if _weather_cache["data"] and (now - _weather_cache["ts"] < WEATHER_TTL_SECONDS):
        return jsonify(_weather_cache["data"])

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={WEATHER_LAT}&longitude={WEATHER_LON}"
        "&current=temperature_2m,weather_code"
        "&timezone=Europe%2FRome"
    )

    try:
        r = requests.get(url, timeout=6)
        r.raise_for_status()
        j = r.json()
        cur = j.get("current", {}) or {}

        data = {
            "ok": True,
            "time": cur.get("time"),
            "temp": cur.get("temperature_2m"),
            "code": cur.get("weather_code"),
        }
        _weather_cache["ts"] = now
        _weather_cache["data"] = data
        return jsonify(data)

    except Exception:
        # se fallisce, restituisci cache se presente (così UI non “muore”)
        if _weather_cache["data"]:
            cached = dict(_weather_cache["data"])
            cached["ok"] = False
            cached["error"] = "fetch_failed"
            return jsonify(cached), 200
        return jsonify({"ok": False, "error": "fetch_failed"}), 200


# ====== MAIN ======

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
